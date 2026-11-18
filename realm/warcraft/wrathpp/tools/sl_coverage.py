#!/usr/bin/env python3
"""Where Wrath++ stands against Shadowlands' creator (the user's standing rule: every option Shadowlands' creator has for a race
and sex is in Wrath++'s creator and is drawn): for every race and sex the creator has, every option Shadowlands gives that model,
what carries it here and what of it is not carried, computed from the data and not from a list kept by hand.

    python3 tools/sl_coverage.py geosets LOOKS.json RACES.json CACHE OUT.json
        the retail models' geosets and the texture types their batches draw with (wago.tools' files by id, through CACHE)
    python3 tools/sl_coverage.py report CSV_DIR LOOKS.json RACES.json OUT.json OUT.md [--geosets G.json] [--package CLIENT_DIR]
        the matrix (LOOKS.json, RACES.json: a looks run's, sl_looks.py races and data; best the ones the package step saved,
        which carry the pieces' texture types)

What is read, and what each column means:
  * Shadowlands' side: ChrCustomizationOption/Choice/Req/Element of the model (ChrModel). A choice is "offered" when its
    requirement's type is 3 (the creator shows it to players: any class, a death knight's, a demon hunter's, by an achievement);
    type 2 is a creature's only, 4 a hidden one, 1 an unlock the creator doesn't list. An option under a category with a
    shapeshift form (Bear Form...) is a druid's form: listed apart, never a gap (3.3.5's forms are fixed creatures).
  * The creator's side: sl_creator.build's own data (what WrathppLooks.lua is written from), so the mechanism is the one the
    creator really has: one of the five numbers 3.3.5 keeps (skin, face, hair, hair colour, feature), a piece (a model of the
    option's geosets or of a collection's, hung on the character), an overlay (a picture on the head or body shell), a texture
    picker (a picture put on a piece), a model variant (another model, given as a display), a style (kept; its colour option
    draws the picture), or none ("Not drawn yet", greyed).
  * What is carried: every element of every offered choice (a geoset, a material on a texture layer, a collection's model, a bone
    set, a conditional model) is put through the rule that reads it (races.py build_model, sl_looks.py overlays_of, parts_of,
    variants_of) and counted as carried or not, with the reason.
  * With --geosets: whether the geosets a number or a piece shows are in the converted model at all (m2.py leaves out a batch
    whose texture type it doesn't keep). With --package: the same checked against the package's own files.
"""
import collections
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_creator   # noqa: E402
import sl_looks     # noqa: E402
import sl_parts     # noqa: E402
from sl_looks import allied   # noqa: E402

DK, DH = 1 << 5, 1 << 11
KEPT_TYPES = {0, 1, 2, 6, 19}                 # m2.py: fixed, body, cape, hair; the eyes go into the body's composite
PIECE_TYPES = {8, 10, 20}                     # sl_parts.geoset_part's keep_types
SLOTS = 8                                     # WrathppCreate.lua's PART_SLOTS, the add-on's MAX_PARTS, the native mod's kPartSlots
TYPE_NAMES = {1: "skin", 2: "cape", 6: "hair", 8: "fur (skin extra)", 10: "customization", 19: "eyes", 20: "jewellery"}
FIELD_NAMES = {"skin": "the skin number", "face": "the face number", "hair": "the hair style number", "haircolor": "the hair colour number",
               "feature": "the feature number"}


def class_kind(mask):
    """Whose a choice is among 3.3.5's classes: "all", "dk" (a death knight's alone), "nodk" (every class but a death knight) or
    "dh" (a demon hunter's or a later class's alone: none of 3.3.5's, everyone's in Wrath++: sl_creator.class_rule)."""
    mask = int(mask or 0)
    if mask in (0, -1):
        return "all"
    mask &= 0xFFF
    if mask & ~DH == 0:
        return "dh"
    if mask & ~DH == DK:
        return "dk"
    if not mask & DK:
        return "nodk"
    return "all"


def sl_counts(tables, choices):
    out = collections.Counter(rows=len(choices))
    for c in choices:
        req = tables.reqs.get(c["ChrCustomizationReqID"])
        kind = req["ReqType"] if req is not None else "3"
        if kind == "3":
            out["offered"] += 1
            out[class_kind(req["ClassMask"]) if req is not None else "all"] += 1
            if req is not None and int(req.get("ReqAchievementID") or 0):
                out["achievement"] += 1
        else:
            out[{"2": "npc", "4": "hidden"}.get(kind, "unlock")] += 1
    return dict(out)


def offered(tables, choice):
    req = tables.reqs.get(choice["ChrCustomizationReqID"])
    return req is None or req["ReqType"] == "3"


class Layers:
    """A model's texture layers: target -> (texture type, section mask)."""

    def __init__(self, tables, chr_model):
        layout = tables.chr_models[str(chr_model)]["CharComponentTextureLayoutID"]
        self.of = {}
        for row in tables.layers:
            if row["CharComponentTextureLayoutsID"] == layout:
                self.of[row["ChrModelTextureTargetID_0"]] = (int(row["TextureType"]), int(row["TextureSectionTypeBitMask"]))

    def kind(self, target):
        return self.of.get(target, (None, None))


def creator_models(csv_dir, looks, races):
    """sl_creator.build's models, each choice with the id of Shadowlands' choice it is ("_id"), and each model's looks spec:
    {key: (creator model, looks model, entry, Shadowlands' race id)}."""
    saved = sl_creator.entry

    def entry(tables, choice, digit):
        e = saved(tables, choice, digit)
        e["_id"] = choice["ID"]
        return e
    sl_creator.entry = entry
    try:
        data = sl_creator.build(csv_dir, looks, races)
    finally:
        sl_creator.entry = saved
    out = {}
    for race in looks["races"].values():
        for sex, model in race["models"].items():
            key = "%d_%d" % (race["race"], int(sex))
            out[key] = (data["models"][key], model, race, race["race"])
    game = sl_creator.game_race_ids()
    for name, entry_ in (races or {}).items():
        if name not in game:
            continue
        alias = entry_.get("alias_of")
        source = (races.get(alias) or looks["races"].get(str(alias))) if alias else entry_
        for sex, model in entry_["models"].items():
            key = "%d_%d" % (game[name], int(sex))
            out[key] = (data["models"][key], model, dict(entry_, key=name), int(source["race"]))
    return out


def mechanism(co):
    """(kind, words) of a creator option."""
    if co is None:
        return "absent", "not in the creator"
    if "field" in co:
        words = "%s (part %d)" % (FIELD_NAMES[co["field"]], co["part"])
        if co.get("geoset"):
            words += " and a piece over it for its colour"
        return "number", words
    if co.get("style"):
        return "style", "a style: kept, drawn by its colour option's picture"
    if co.get("overlay"):
        where = "head and body shells" if co.get("bodyoverlay") else "head shell"
        return "overlay", "a picture on the %s" % where + (" (follows %s)" % ", ".join(co["depends"]) if co.get("depends") else "")
    if co.get("geoset"):
        return "piece", "a piece (a model hung on the character)"
    if co.get("texture"):
        return "picker", "a texture picker (a picture put on a piece)"
    if co.get("variant"):
        return "variant", "a model variant (another model, by a display)"
    return "none", "none: greyed \"Not drawn yet\""


class Model:
    """One race and sex: Shadowlands' options against the creator's."""

    def __init__(self, tables, categories, key, cm, spec, entry, sl_race, geosets=None, package=None, parts_lines=None):
        self.tables, self.categories, self.key, self.cm, self.spec, self.entry, self.sl_race = tables, categories, key, cm, spec, entry, sl_race
        self.chr_model = spec["chr_model"]
        self.layers = Layers(tables, self.chr_model)
        self.geosets = (geosets or {}).get(str(spec["model"]))
        self.all_geosets = geosets or {}
        self.package, self.parts_lines = package, parts_lines or []
        self.aliases = sl_looks.ALIASES.get(sl_race, {})
        self.co = {o["name"]: o for o in cm["options"]}
        self.option_of_choice = {c["ID"]: o for o in tables.options.values() for c in tables.choices[o["ID"]]}
        self.notes = []
        self.regroup = sl_looks.FEATURES.get((sl_race, int(spec["sex"])), allied.FEATURES.get((sl_looks.LEGACY.get(sl_race), int(spec["sex"])), ([], {})))[1]
        self.kept = KEPT_TYPES | {int(k) for k in spec.get("hardcoded", {})} | set(spec.get("keep_types", []))

    # --- Shadowlands' side ---------------------------------------------------------------------------------------------
    def sl_options(self):
        mine = [o for o in self.tables.options.values() if o["ChrModelID"] == str(self.chr_model)]
        return sorted(mine, key=lambda o: int(o["OrderIndex"]))

    def today(self, asked):
        return self.aliases.get(asked, asked)

    # --- what a choice's elements are, and whether the option's mechanism carries each ----------------------------------
    def elements(self, choice):
        t = self.tables
        out = []
        for e in t.elements[choice["ID"]]:
            related = e["RelatedChrCustomizationChoiceID"]
            if e["ChrCustomizationGeosetID"] != "0" and e["ChrCustomizationGeosetID"] in t.geosets:
                g = t.geoset_of(e)
                if g % 100:
                    out.append(("geoset", g, related))
            if e["ChrCustomizationMaterialID"] != "0" and e["ChrCustomizationMaterialID"] in t.materials:
                target, files = t.material_files(e)
                if self.layers.kind(target)[0] is not None:       # (a target the model's layout has no layer for draws nothing in Shadowlands either)
                    out.append(("material", target, related, files[0] if files else 0))
            if e["ChrCustomizationSkinnedModelID"] != "0" and e["ChrCustomizationSkinnedModelID"] in t.skinned:
                sm = t.skinned[e["ChrCustomizationSkinnedModelID"]]
                out.append(("model", int(sm["CollectionsFileDataID"]), related, int(sm["GeosetType"]) * 100 + int(sm["GeosetID"])))
            if e.get("ChrCustomizationBoneSetID", "0") not in ("0", ""):
                out.append(("boneset", int(e["ChrCustomizationBoneSetID"]), related))
            if e.get("ChrCustomizationCondModelID", "0") not in ("0", ""):
                out.append(("condmodel", int(e["ChrCustomizationCondModelID"]), related))
            if e.get("ChrCustomizationDisplayInfoID", "0") not in ("0", ""):
                out.append(("displayinfo", int(e["ChrCustomizationDisplayInfoID"]), related))
        return out

    def related_name(self, related):
        o = self.option_of_choice.get(related)
        return o["Name_lang"] if o else "?"

    def carried(self, o, co, kind, choice, element):
        """(carried, why not) for one element of one choice of option [o] under the creator's mechanism [kind]."""
        what = element[0]
        name = o["Name_lang"]
        spec = self.spec
        if what in ("boneset", "displayinfo"):
            return False, {"boneset": "a bone set (ChrCustomizationBoneSet): the native mod sets no bones by choice",
                           "displayinfo": "a display (ChrCustomizationDisplayInfo)"}[what]
        if what == "condmodel":
            if kind == "variant":
                return True, ""
            return False, "a conditional model (ChrCustomizationCondModel)"
        if kind == "number":
            field, part = co["field"], co["part"]
            if field == "skin":
                colour = part == len(self.cm["fields"]["skin"])
                if what == "material":
                    target = element[1]
                    if colour and target in (allied.TARGET_BODY, allied.TARGET_PELVIS, allied.TARGET_TORSO):
                        return True, ""
                    if colour and spec.get("fur") and self.layers.kind(target)[0] == 8:
                        return True, ""
                    if not colour and target == allied.TARGET_TATTOO:
                        return True, ""
                    return False, "a material on target %s (%s)" % (target, self.layer_words(target))
                return False, "a geoset (%d)" % element[1] if what == "geoset" else what
            if field == "face" and part == 1:
                if what == "material" and element[1] == allied.TARGET_FACE:
                    return True, ""
                return False, ("a material on target %s (%s)" % (element[1], self.layer_words(element[1])) if what == "material" else "%s %s" % (what, element[1]))
            if field == "face":
                if what == "material" and element[1] in (allied.TARGET_EYES, allied.TARGET_EYE_FACE):
                    return True, ""
                if what == "geoset" and element[1] // 100 == 33:
                    return True, ""                           # the eyeballs: always drawn (races.py folds 3301 into geoset 0)
                if what == "geoset" and element[1] // 100 == allied.GLOW_GROUP:
                    first = spec["eyes"][0]["choice"] if spec.get("eyes") else None
                    return (True, "") if choice["ID"] == first else (False, "its eye glow's shape (geoset %d): the model keeps the first eye colour's" % element[1])
                return False, ("a material on target %s (%s)" % (element[1], self.layer_words(element[1])) if what == "material" else "%s %s" % (what, element[1]))
            if field == "hair":
                if what == "geoset":
                    first = [e[1] for e in self.elements(choice) if e[0] == "geoset" and e[1] < 100][:1]
                    if element[1] < 100 and first and element[1] == first[0]:
                        return True, ""
                    return False, "a second geoset (%d%s): 3.3.5's hair table holds one a style" % (
                        element[1], ", with %s" % self.related_name(element[2]) if element[2] != "0" else "")
                if what == "material":
                    if self.layers.kind(element[1])[0] == 1:
                        return True, ""                       # the scalp (races.py: a layer over the face)
                    return False, "a material on target %s (%s)" % (element[1], self.layer_words(element[1]))
                return False, "%s %s" % (what, element[1])
            if field == "haircolor":
                if what == "material":
                    if element[1] == allied.TARGET_HAIR:
                        if element[2] == "0":
                            return True, ""
                        if co.get("parts_with") and self.related_name(element[2]) in co["parts_with"]:
                            return True, ""
                        firsts = [e for e in self.elements(choice) if e[0] == "material" and e[1] == allied.TARGET_HAIR][:1]
                        if firsts and firsts[0] == element:
                            return True, ""
                        return False, "the hair texture it has with %s: the number holds the first" % self.related_name(element[2])
                    if self.layers.kind(element[1])[0] == 1:
                        return True, ""                       # a scalp for a style
                    return False, "a material on target %s (%s)" % (element[1], self.layer_words(element[1]))
                return False, "%s %s" % (what, element[1])
            if field == "feature":
                if what == "geoset":
                    group = self.regroup.get(element[1] // 100, element[1] // 100)
                    if group in (1, 2, 3, 16):
                        return True, ""
                    return False, "a geoset of group %d (%d): 3.3.5's feature table holds groups 1, 2, 3 and 16" % (element[1] // 100, element[1])
                if what == "material" and co.get("geoset"):
                    return True, ""
                return False, ("a material on target %s (%s)" % (element[1], self.layer_words(element[1])) if what == "material" else "%s %s" % (what, element[1]))
        if kind == "overlay":
            if what == "material":
                ttype, mask = self.layers.kind(element[1])
                if ttype == 1 and (mask in sl_looks.HEAD_MASKS or mask in sl_looks.BODY_MASKS or mask in getattr(sl_looks, "SECTION_MASKS", ())):
                    return True, ""
                return False, "a material on target %s (%s)" % (element[1], self.layer_words(element[1]))
            return False, "%s %s" % (what, element[1])
        if what == "material" and str(self.layers.kind(element[1])[0]) in spec.get("hardcoded", {}) and kind in ("piece", "number"):
            first = self.tables.choices[o["ID"]][0]["ID"] == choice["ID"] or len({e[3] for c in self.tables.choices[o["ID"]] for e in self.elements(c)
                                                                                  if e[0] == "material" and e[1] == element[1]}) < 2
            if first:
                return True, ""                               # the model's own fixed texture of that type (races.py: hardcoded)
        if kind == "piece":
            if what == "geoset":
                return True, ""
            if what == "model":
                part = next((p for p in spec.get("parts", []) if p["name"] == name), None)
                if part and part.get("skinned") == element[1]:
                    return True, ""
                return False, "a collection's model (file %d)" % element[1]
            if what == "material":
                return False, "a material on target %s (%s)" % (element[1], self.layer_words(element[1]))
        if kind == "picker":
            if what == "material":
                ttype, _ = self.layers.kind(element[1])
                if ttype not in (None, 1) and element[2] == "0":
                    return True, ""
                return False, "a material on target %s (%s)%s" % (element[1], self.layer_words(element[1]),
                                                                  " with %s" % self.related_name(element[2]) if element[2] != "0" else "")
            return False, "%s %s" % (what, element[1])
        if kind == "variant":
            if what == "geoset":
                return True, ""
        return False, ("a material on target %s (%s)" % (element[1], self.layer_words(element[1])) if what == "material" else "%s %s" % (what, element[1]))

    def layer_words(self, target):
        ttype, mask = self.layers.kind(target)
        if ttype is None:
            return "no layer of the model's layout"
        return "%s texture, sections mask %s" % (TYPE_NAMES.get(ttype, "type %d" % ttype), mask)

    # --- the geometry: is a geoset in the converted model ---------------------------------------------------------------
    def geometry(self, geoset, piece=False, file=None):
        """"" when the geoset's batches are kept by the converter, else why not (needs --geosets)."""
        table = self.all_geosets.get(str(file)) if file else self.geosets
        if table is None:
            return ""
        types = table.get(str(geoset))
        if types is None:
            return "the model has no geoset %d" % geoset
        kept = self.kept | (PIECE_TYPES if piece else set())
        lost = [t for t in types if t not in kept]
        if not lost:
            return ""
        words = ", ".join(TYPE_NAMES.get(t, "type %d" % t) for t in sorted(set(lost)))
        if len(lost) == len(types):
            return "geoset %d is left out of the converted model: it draws with the %s texture, which the converter doesn't keep" % (geoset, words)
        return "geoset %d's part drawn with the %s texture is left out" % (geoset, words)

    # --- one option -----------------------------------------------------------------------------------------------------
    def option(self, o):
        t = self.tables
        name = o["Name_lang"]
        category = self.categories.get(o["ChrCustomizationCategoryID"])
        rows = sorted(t.choices[o["ID"]], key=sl_creator.ui_order)
        rec = {"name": name, "id": int(o["ID"]), "category": (category or {}).get("CategoryName_lang", "").split(" (")[0],
               "type": "switch" if int(o.get("OptionType") or 0) == 1 else "list", "sl": sl_counts(t, rows), "issues": []}
        if category is not None and int(category.get("SpellShapeshiftFormID") or 0):
            rec["form"] = True
            return rec
        co = self.co.get(name)
        kind, words = mechanism(co)
        rec["mechanism"], rec["mechanism_words"] = kind, words
        offer = [c for c in rows if offered(t, c)]
        # what the option's offered choices change in Shadowlands
        does = collections.Counter()
        for c in offer:
            for e in self.elements(c):
                does[e[0]] += 1
        rec["does"] = dict(does)
        if co is None:
            rec["creator"] = None
            rec["greyed"] = "absent"
            rec["drawn"] = "no"
            if len(offer) >= 2:
                rec["issues"].append(self.why_absent(o, offer, does))
            else:
                rec["drawn"] = "n/a"
                rec["note"] = "Shadowlands offers %d choice%s: nothing to choose" % (len(offer), "" if len(offer) == 1 else "s")
            return rec
        ids = [c.get("_id") for c in co["choices"]]
        rec["creator"] = {"choices": len(co["choices"]), "dk": sum(1 for c in co["choices"] if c.get("c") == "dk"),
                          "nodk": sum(1 for c in co["choices"] if c.get("c") == "nodk"), "reg": co.get("reg")}
        if "field" in co:
            rec["creator"]["field"], rec["creator"]["part"] = co["field"], co["part"]
        # the choices: Shadowlands' offered against the creator's
        offer_ids = {c["ID"] for c in offer}
        missing = [c for c in offer if c["ID"] not in ids]
        extra = [i for i in ids if i not in offer_ids]
        rec["choices"] = {"offered": len(offer), "creator": len(ids), "missing": len(missing), "extra": len(extra)}
        if missing:
            rec["issues"].append(self.why_missing(o, co, missing))
        if extra:
            rec["choices"]["extra_words"] = self.extra_words(extra)
        # greyed?
        rec["greyed"] = "no"
        if kind == "none":
            rec["greyed"] = "always: \"Not drawn yet\""
            rec["drawn"] = "no"
            rec["issues"].append(self.why_later(o, offer, does))
            return rec
        if kind == "number" and co["field"] in ("hair", "haircolor") and not self.spec.get("hair_colors") and not self.spec.get("hair_rows"):
            rec["greyed"] = "always: \"None for this character\""
            rec["issues"].append({"code": "no-hair-rows", "severity": "no",
                                  "text": "the game counts no hair styles for this race and sex: CharSections has no hair row for it (a hair row is a style and a "
                                          "colour, and the model has no hair colours), so the row is greyed and the client's SetHairStyle refuses every style",
                                  "rule": "sl_looks.py table_rows: hair rows are written for each hair colour (none here)",
                                  "fix": "the hair style number: a hair row a style with one colour and no hair texture (the client skips an empty name)"})
        # every element of every offered choice through the mechanism
        lost = collections.Counter()
        whole = 0
        conditional = set()
        for c in offer:
            if c["ID"] not in ids and kind == "number":
                continue
            ok = True
            for e in self.elements(c):
                carried, why = self.carried(o, co, kind, c, e)
                if not carried:
                    ok = False
                    lost[why] += 1
                elif kind == "piece" and e[0] == "geoset" and e[2] != "0":
                    conditional.add(self.related_name(e[2]))
            whole += ok
        rec["carried"] = {"choices": whole, "of": len([c for c in offer if c["ID"] in ids or kind != "number"])}
        classes = collections.defaultdict(collections.Counter)
        for why, n in lost.items():
            classes[self.class_of(why)][why] = n
        for code, whys in sorted(classes.items()):
            rec["issues"].append({"code": code, "severity": "native" if code.startswith("needs-") else "minor" if code == "eye-glow-shape" else "partly",
                                  "text": "not carried by %s: %s" % (words.split(" (")[0], "; ".join("%s (x%d)" % (w, n) for w, n in whys.most_common(4))),
                                  "rule": self.rule_of(kind, co), "fix": self.fix_for(whys)})
        if conditional and not co.get("cond"):
            rec["issues"].append({"code": "conditional-geosets", "severity": "partly",
                                  "text": "its geosets are one for each choice of %s (Shadowlands shows the one that fits); the piece shows all of a choice's at once"
                                          % ", ".join(sorted(conditional)),
                                  "rule": "sl_looks.py parts_of: tables.choice_geosets takes every geoset element whatever it is related to; "
                                          "sl_parts.py geoset_part puts them all under one choice's ids",
                                  "fix": "a piece: a block of geoset ids for each pair (choice, the other option's choice), the creator giving the block's number"})
        self.geometry_issues(o, co, kind, offer, ids, rec)
        self.wiring_issues(o, co, kind, rec)
        severities = [i["severity"] for i in rec["issues"]]
        rec["drawn"] = "no" if "no" in severities else "partly" if "partly" in severities else "native" if "native" in severities else "yes"
        return rec

    def rule_of(self, kind, co):
        if kind == "number":
            return "races.py build_model (the five numbers: what a number's rows carry)" + ("; sl_looks.py FEATURES (the feature groups)" if co["field"] == "feature" else "")
        return {"overlay": "sl_looks.py overlays_of (a skin layer whose sections are the head's or the body's)", "piece": "sl_looks.py parts_of (geosets, or one collection's model)",
                "picker": "sl_looks.py parts_of (a layer of another texture type, related to nothing)", "variant": "sl_looks.py variants_of",
                "style": "sl_looks.py overlays_of (a style has no picture of its own)"}.get(kind, "")

    @staticmethod
    def class_of(why):
        if "bone set" in why:
            return "needs-bone-sets"
        if "conditional model" in why or "a display" in why:
            return "needs-models"
        if "eye glow" in why:
            return "eye-glow-shape"
        if why.startswith("a material"):
            return "texture-not-carried"
        if "collection" in why:
            return "collection-model-not-carried"
        return "geoset-not-carried"

    def fix_for(self, lost):
        words = " ".join(lost)
        if "bone set" in words:
            return "needs the native mod: bones set by choice (wxl.m2 watch_bones)"
        if "conditional model" in words:
            return "a model variant (sl_looks.py variants_of)"
        if "fur" in words:
            return "the skin number: the skin row's second texture (3.3.5's skin extra, type 8)"
        if "jewellery" in words or "customization texture" in words:
            return "a texture picker on a piece that takes it"
        if "collection" in words:
            return "a piece of the collection's model (sl_parts.geoset_part, skinned)"
        if "geoset" in words:
            return "a piece of those geosets (sl_looks.py parts_of)"
        if "skin texture" in words:
            return "an overlay picture on the head or body shell (sl_looks.py overlays_of)"
        return "a mechanism of its own"

    def why_absent(self, o, offer, does):
        t = self.tables
        avail = [c for c in offer if t.available(c)]
        if self.categories.get(o["ChrCustomizationCategoryID"]) is None:
            text = "its category is not in ChrCustomizationCategory"
        else:
            text = "the creator lists an option only with two choices or more: %d here" % len(avail)
        return {"code": "absent", "severity": "no", "text": text, "rule": "sl_creator.py build_model (len(option[\"choices\"]) < 2)",
                "fix": "list it" if len(avail) >= 2 else "nothing to choose"}

    def why_missing(self, o, co, missing):
        t = self.tables
        name = o["Name_lang"]
        spec = self.spec
        reasons = collections.Counter()
        for c in missing:
            req = t.reqs.get(c["ChrCustomizationReqID"])
            who = class_kind(req["ClassMask"]) if req is not None else "all"
            if self.entry.get("alias_of") and name in ("Skin Color", "Face"):
                reasons["by design: this race is another's models with a subset of its skins and faces"] += 1
            elif name == "Eye Color":
                blind = False
                for b in t.option_choices(self.chr_model, "Blindfold", only_available=False):
                    blind = blind or any(e["RelatedChrCustomizationChoiceID"] == c["ID"] for e in t.elements[b["ID"]])
                files = [f for _, fs in t.choice_materials(c, allied.TARGET_EYES) for f in fs]
                if blind:
                    reasons["a demon hunter's eyes under a blindfold (races.py build_model: related to a Blindfold)"] += 1
                elif c["Flags"] != "0":
                    reasons["marked hidden in the creator (choice Flags %s: races.py build_model leaves it out unless unlocked)%s" % (
                        c["Flags"], ", a %s's" % {"dk": "death knight", "dh": "demon hunter"}.get(who, "") if who in ("dk", "dh") else "")] += 1
                elif not files:
                    reasons["no eye texture"] += 1
                else:
                    reasons["past 3.3.5's 255 faces: %d faces x %d eye colours kept (races.py build_model: limit = 255 // faces)" % (len(spec["faces"]), len(spec["eyes"]))] += 1
            elif name == self.today("Hair Color"):
                reasons["no hair texture of its own (races.py build_model: a hair colour needs a material on the hair's target)"] += 1
            elif name == self.today("Skin Color"):
                reasons["no body texture"] += 1
            elif "field" in co and co["field"] == "skin":
                reasons["a tattoo with no picture on the tattoo's target (sl_creator.py digits_of)"] += 1
            elif name in sl_looks.AVAILABLE_ONLY.get((self.sl_race, int(spec["sex"])), ()):
                reasons["sl_looks.py AVAILABLE_ONLY"] += 1
            else:
                reasons["not in the looks"] += 1
        text = "%d of Shadowlands' offered choices are not in the creator: %s" % (len(missing), "; ".join("%s (x%d)" % (w, n) for w, n in reasons.most_common()))
        design = all(w.startswith("by design") or "demon hunter's eyes" in w for w in reasons)
        return {"code": "choices-missing", "severity": "ok" if design else "partly", "text": text,
                "rule": "races.py build_model", "fix": "" if design else "more of the number's room, or a category of its own"}

    def extra_words(self, extra):
        t = self.tables
        kinds = collections.Counter()
        for i in extra:
            c = t.choice_by_id.get(i)
            if c is None:
                kinds["Wrath++'s own (added)"] += 1
                continue
            req = t.reqs.get(c["ChrCustomizationReqID"])
            kinds[{"2": "a creature's only in Shadowlands", "4": "hidden in Shadowlands", "1": "an unlock in Shadowlands"}.get(req["ReqType"] if req else "3", "other")] += 1
        return "; ".join("%d %s" % (n, w) for w, n in kinds.most_common())

    def why_later(self, o, offer, does):
        """Why no rule took the option, and what would draw it."""
        t = self.tables
        mine = {c["ID"] for c in offer}
        if not does:
            users = collections.Counter()
            for other in self.sl_options():
                if other["ID"] == o["ID"]:
                    continue
                for c in t.choices[other["ID"]]:
                    for e in t.elements[c["ID"]]:
                        if e["RelatedChrCustomizationChoiceID"] in mine and e["ChrCustomizationMaterialID"] != "0":
                            target, _ = t.material_files(e)
                            users[(other["Name_lang"], target)] += 1
            if users:
                (other, target), _ = users.most_common(1)[0]
                oc = self.co.get(other)
                okind, _ = mechanism(oc)
                fix = "a second part of %s (%s x %s), as a face number is a face and an eye colour" % (
                    FIELD_NAMES.get(oc["field"], "the number"), other, o["Name_lang"]) if okind == "number" else "the other option's picture chosen by this one (a style)"
                return {"code": "later", "severity": "no",
                        "text": "its choices have no elements of their own: %s's materials on target %s (%s) are one for each of them, and the looks take the first" % (
                            other, target, self.layer_words(target)),
                        "rule": "sl_looks.py parts_of and overlays_of see nothing to draw; races.py build_model reads %s's first material only" % other, "fix": fix}
            return {"code": "later", "severity": "no", "text": "its choices change nothing the tables name (no geoset, material or model)",
                    "rule": "sl_looks.py parts_of", "fix": "unknown: read the game's own handling"}
        layers = collections.Counter()
        files = set()
        for c in offer:
            for e in self.elements(c):
                if e[0] == "material":
                    layers[(e[1],) + self.layers.kind(e[1]) + (e[2] != "0",)] += 1
                elif e[0] == "model":
                    files.add(e[1])
        if layers:
            (target, ttype, mask, related), _ = layers.most_common(1)[0]
            if ttype == 1:
                return {"code": "later", "severity": "no",
                        "text": "pictures on the skin's layer of target %s, whose sections (mask %s) are neither the head's (%s) nor the body's (%s)" % (
                            target, mask, "/".join(str(m) for m in sl_looks.HEAD_MASKS), "/".join(str(m) for m in sl_looks.BODY_MASKS)),
                        "rule": "sl_looks.py overlays_of: mask not in HEAD_MASKS and not in BODY_MASKS",
                        "fix": "an overlay picture on the body shell, the section's picture put at its place in the skin (CharComponentTextureSections)"}
            if ttype is None:
                return {"code": "later", "severity": "no", "text": "materials on target %s, which the model's layout has no layer for" % target,
                        "rule": "sl_looks.py parts_of: kinds.get(target) is None", "fix": "unknown: the target is drawn by something other than a layer"}
            return {"code": "later", "severity": "no",
                    "text": "pictures of the %s texture (target %s)%s" % (TYPE_NAMES.get(ttype, "type %d" % ttype), target, ", each with another option's choice" if related else ""),
                    "rule": "sl_looks.py parts_of: a picker is a layer of one other texture type, related to nothing, on a model with pieces",
                    "fix": "a texture picker (the picture put on the pieces, or on the model's own texture of that type)"}
        if len(files) > 1:
            return {"code": "later", "severity": "no", "text": "models of %d collections" % len(files), "rule": "sl_looks.py parts_of: len(files) == 1",
                    "fix": "a piece for each collection's model"}
        kinds = ", ".join("%s x%d" % kv for kv in sorted(does.items()))
        needs = {"boneset": "needs the native mod: bones set by choice", "condmodel": "a model variant (sl_looks.py variants_of)",
                 "displayinfo": "a display"}
        fix = next((v for k, v in needs.items() if k in does), "a piece of its geosets (sl_looks.py parts_of)")
        return {"code": "later", "severity": "no", "text": "its choices are %s, which no rule of the looks takes" % kinds, "rule": "sl_looks.py parts_of, overlays_of, variants_of",
                "fix": fix}

    # --- geometry and wiring ---------------------------------------------------------------------------------------------
    def geometry_issues(self, o, co, kind, offer, ids, rec):
        spec = self.spec
        name = o["Name_lang"]
        found = collections.Counter()
        choices_hit = 0
        if kind == "number" and co["field"] == "hair":
            for h in spec["hair"]:
                why = self.geometry(h["geoset"]) if h["geoset"] else ""
                if why:
                    found[why.split(": ", 1)[-1] if ": " in why else why] += 1
                    choices_hit += 1
        elif kind == "number" and co["field"] == "feature":
            for c in self.tables.option_choices(self.chr_model, name, only_available=False):
                hit = False
                for e in self.elements(c):
                    if e[0] == "geoset" and self.regroup.get(e[1] // 100, e[1] // 100) in (1, 2, 3, 16):
                        why = self.geometry(e[1])
                        if why:
                            found[why.split(": ", 1)[-1] if ": " in why else why] += 1
                            hit = True
                choices_hit += hit
        elif kind == "piece":
            part = next((p for p in spec.get("parts", []) if p["name"] == name), None)
            if part:
                for c in part["choices"]:
                    hit = False
                    for g in c["geosets"]:
                        why = self.geometry(g, piece=True, file=part.get("skinned"))
                        if why:
                            found[why.split(": ", 1)[-1] if ": " in why else why] += 1
                            hit = True
                    choices_hit += hit
        if found:
            total = sum(found.values())
            whole = sum(n for w, n in found.items() if "is left out of the converted model" in w or w.startswith("it draws") or "no geoset" in w)
            rec["issues"].append({"code": "geometry-left-out", "severity": "no" if whole == total and kind == "number" and choices_hit >= len(ids) - 1 else "partly",
                                  "text": "%d of its choices lose geometry in the converted model: %s" % (choices_hit, "; ".join("%s (x%d)" % (w, n) for w, n in found.most_common(3))),
                                  "rule": "m2.py convert: a batch whose texture type is not kept (KEPT_TYPES, keep_types, hardcoded) is left out",
                                  "fix": "the skin number's second texture (3.3.5's skin extra, type 8) for the fur; a hardcoded or picked texture for the rest"})

    def wiring_issues(self, o, co, kind, rec):
        spec = self.spec
        name = o["Name_lang"]
        if kind in ("overlay", "piece", "picker", "variant", "style") and not co.get("reg"):
            rec["issues"].append({"code": "no-registry-category", "severity": "partly",
                                  "text": "no registry category yet: the creator draws it, the realm does not keep it and the world does not draw it",
                                  "rule": "registry_parts.py (registry/parts_ids.json has no key for it)", "fix": "regenerate the registry from this looks run"})
        if kind == "picker":
            picker = next((p for p in spec.get("pickers", []) if p["name"] == name), None)
            takers = [p["name"] for p in spec.get("parts", []) if 13 in spec.get("part_types", {}).get(p["name"], [])]
            first = spec.get("pickers", [{}])[0].get("name") == name
            if picker and "part_types" in spec:
                if not takers or not first:
                    rec["issues"].append({"code": "picker-reaches-nothing", "severity": "no",
                                          "text": ("no piece of the model takes a picked texture (type 13)" if not takers else "the pieces take the model's first picker, %s" % spec["pickers"][0]["name"])
                                          + ": choosing it changes nothing",
                                          "rule": "sl_parts.py write_parts_table and sl_creator.py build_model: a piece takes pickers[0] when it has a type 13 texture",
                                          "fix": "the option's own geometry drawn as a piece in the colour chosen (sl_looks.py FEATURE_PARTS), or the picture put on the model's own texture of that type"})
                elif picker["type"] not in (10, 20):
                    rec["issues"].append({"code": "picker-wrong-slot", "severity": "partly",
                                          "text": "a picker of the %s texture is put on the pieces' customization texture (%s)" % (TYPE_NAMES.get(picker["type"], picker["type"]), ", ".join(takers)),
                                          "rule": "sl_parts.py write_parts_table: next(iter(pickers.values())) whatever the picker's texture type",
                                          "fix": "a picker goes to the pieces' texture of its own type"})
        if kind == "piece":
            part = next((p for p in spec.get("parts", []) if p["name"] == name), None)
            table = self.all_geosets.get(str(part.get("skinned"))) if part and part.get("skinned") else self.geosets
            fur = sorted({g for c in (part or {}).get("choices", []) for g in c["geosets"] if 8 in (table or {}).get(str(g), [])})
            if fur and not spec.get("fur"):
                rec["issues"].append({"code": "fur-drawn-with-the-skin", "severity": "partly",
                                      "text": "%d of its geosets draw with the fur texture (type 8); the piece is given the skin's picture in its place (%s)" % (
                                          len(fur), ", ".join(str(g) for g in fur[:8])),
                                      "rule": "sl_parts.py TYPE_SLOTS (8 -> 11) and write_parts_table's K lines (the skins)",
                                      "fix": "the skin's fur texture (its second texture) given to the piece"})
        if kind == "piece" and "part_types" in spec:
            types = spec["part_types"].get(name, [])
            if 13 in types and not spec.get("pickers"):
                rec["issues"].append({"code": "piece-without-its-texture", "severity": "partly",
                                      "text": "the piece draws with a customization texture (jewellery) and the model has no picker to give it one: nothing is put on it",
                                      "rule": "sl_parts.py write_parts_table: picker_category 0", "fix": "the model's own jewellery texture (hardcoded[\"20\"]) given to the piece"})
        if kind in ("overlay", "piece") and co.get("slot", 0) > SLOTS:
            rec["issues"].append({"code": "past-the-slots", "severity": "partly",
                                  "text": "slot %d of %d: the creator and the world hang %d parts on a character, and this option comes after them" % (co["slot"], SLOTS, SLOTS),
                                  "rule": "WrathppCreate.lua W.Look (PART_SLOTS), init.lua partsOf (MAX_PARTS), Native.cpp kPartSlots",
                                  "fix": "no slot spent on a choice that shows nothing; more slots in the native mod"})
        if kind == "overlay" and len(co.get("depends", [])) > 1 and not co.get("styles_by_shell"):
            rec["issues"].append({"code": "two-styles-one-category", "severity": "partly",
                                  "text": "its head pictures follow %s and its body pictures %s; the parts table names one style for both, so in the world the head's "
                                          "picture is chosen by the body's style" % (co["depends"][-1], co["depends"][0]),
                                  "rule": "sl_parts.py write_parts_table: style = ids.get(depends[0]) for the P and the U line alike",
                                  "fix": "each shell's line names the style its pictures are keyed by"})


def slots(cm):
    """The slot each option takes in the creator (W.Look's order: the head shells, the body shells, then the pieces)."""
    slot = 0
    for body in (False, True):
        for o in cm["options"]:
            if o.get("overlay") and "field" not in o and (not body or o.get("bodyoverlay")):
                slot += 1
                o["slot"] = max(o.get("slot", 0), slot)
    for o in cm["options"]:
        if o.get("geoset"):
            slot += 1
            o["slot"] = slot
    return slot


def build(csv_dir, looks, races, geosets=None, package=None):
    tables = sl_looks.Tables(csv_dir)
    categories = {c["ID"]: c for c in allied.rows(csv_dir, "ChrCustomizationCategory")}
    models = creator_models(csv_dir, looks, races)
    out = {"build": sl_looks.BUILD, "models": {}}
    for key in sorted(models, key=lambda k: tuple(int(x) for x in k.split("_"))):
        cm, spec, entry, sl_race = models[key]
        used = slots(cm)
        m = Model(tables, categories, key, cm, spec, entry, sl_race, geosets, package)
        rec = {"key": key, "name": cm["name"], "race": cm["race"], "sex": cm["sex"], "chr_model": spec["chr_model"], "shadowlands_race": sl_race,
               "alias_of": entry.get("alias_of"), "slots": used, "options": [], "forms": [], "notes": []}
        for o in m.sl_options():
            r = m.option(o)
            (rec["forms"] if r.get("form") else rec["options"]).append(r)
        if used > SLOTS:
            rec["notes"].append("%d slots asked for, %d hung: the options after slot %d are not drawn while the ones before them are on" % (used, SLOTS, SLOTS))
        fur = [g for g, types in (m.geosets or {}).items() if 8 in types and 8 not in m.kept]
        if fur:
            rec["notes"].append("the fur (texture type 8, the skin's second texture): %d geosets of the model draw with it and are left out or cut (%s)" % (
                len(fur), ", ".join(sorted(fur, key=int)[:14]) + ("..." if len(fur) > 14 else "")))
        out["models"][key] = rec
    return out


# --- the retail models' geosets ---------------------------------------------------------------------------------------

def chunks_of(data):
    out, at = {}, 0
    while at + 8 <= len(data):
        cid = data[at:at + 4].decode("latin1")
        size = struct.unpack_from("<I", data, at + 4)[0]
        out[cid] = data[at + 8:at + 8 + size]
        at += 8 + size
    return out


def model_geosets(read, file_id):
    """{geoset id: sorted texture types its batches draw with} of a retail model (its first skin)."""
    c = chunks_of(read(file_id))
    md = c["MD21"]
    tc, to = struct.unpack_from("<II", md, 0x50)
    types = [struct.unpack_from("<I", md, to + i * 16)[0] for i in range(tc)]
    lc, lo = struct.unpack_from("<II", md, 0x80)
    look = struct.unpack_from("<%dh" % lc, md, lo)
    skin = read(struct.unpack_from("<I", c["SFID"], 0)[0])
    ns, os_ = struct.unpack_from("<II", skin, 28)
    nb, ob = struct.unpack_from("<II", skin, 36)
    ids = [struct.unpack_from("<H", skin, os_ + i * 48)[0] for i in range(ns)]
    out = {i: set() for i in ids}
    for i in range(nb):
        sec, = struct.unpack_from("<H", skin, ob + i * 24 + 4)
        count, first = struct.unpack_from("<HH", skin, ob + i * 24 + 14)
        # (3.3.5 draws a batch's first texture: m2.py keeps a batch by it)
        if sec < len(ids) and first < len(look) and 0 <= look[first] < len(types):
            out[ids[sec]].add(types[look[first]])
    return {str(k): sorted(v) for k, v in sorted(out.items())}


def geosets_of(looks, races, cache):
    import package as allied_package
    read = allied_package.cached(cache, allied_package.wago)
    files = set()
    for entry in list(looks["races"].values()) + list((races or {}).values()):
        for m in entry["models"].values():
            files.add(m["model"])
            files.update(p["skinned"] for p in m.get("parts", []) if p.get("skinned"))
    return {str(f): model_geosets(read, f) for f in sorted(files)}


# --- the report ---------------------------------------------------------------------------------------------------------

STATUS_WORDS = {"yes": "drawn", "partly": "partly", "no": "NOT drawn", "n/a": "-", "native": "drawn, but for what needs the native mod"}


def choice_words(r):
    s = r["sl"]
    words = "%d" % s.get("offered", 0)
    extra = ["%d a death knight's" % s["dk"] if s.get("dk") else "", "%d a demon hunter's" % s["dh"] if s.get("dh") else "",
             "%d by achievement" % s["achievement"] if s.get("achievement") else ""]
    extra = [e for e in extra if e]
    return words + (" (%s)" % ", ".join(extra) if extra else "")


def markdown(cov):
    lines = ["# Wrath++ against Shadowlands' creator: the coverage matrix", "",
             "Made by `realm/warcraft/wrathpp/tools/sl_coverage.py` from Shadowlands' tables (%s), the looks' data and the retail models' geosets. "
             "\"Offered\" is what Shadowlands' creator shows players (requirement type 3); a death knight's and a demon hunter's own choices are counted in it and named. "
             "\"Drawn\" is what the data says reaches the 3.3.5 game: nothing here was seen in the game." % cov["build"], ""]
    totals = collections.Counter()
    codes = collections.defaultdict(list)
    for m in cov["models"].values():
        for r in m["options"]:
            if r.get("drawn") == "n/a":
                continue
            totals[r["drawn"]] += 1
            for i in r["issues"]:
                if i["severity"] not in ("ok",):
                    codes[i["code"]].append((m["name"] if not m["alias_of"] else "%s (%s)" % (m["key"], m["name"]), r["name"], i))
    lines += ["## Summary", "", "%d races and sexes, %d options that are a character's looks: %d drawn whole, %d drawn but for a part that needs the native mod "
              "(bone sets), %d partly, %d not drawn." % (len(cov["models"]), sum(totals.values()), totals["yes"], totals["native"], totals["partly"], totals["no"]), ""]
    lines += ["| Gap | Options | Where |", "|---|---|---|"]
    for code, hits in sorted(codes.items(), key=lambda kv: -len(kv[1])):
        where = collections.OrderedDict()
        for model, option, _ in hits:
            where.setdefault(model, []).append(option)
        lines.append("| %s | %d | %s |" % (code, len(hits), "; ".join("%s: %s" % (k, ", ".join(v)) for k, v in where.items())))
    lines.append("")
    for key, m in cov["models"].items():
        lines += ["## %s %s (race %d, ChrModel %d%s)" % (m["key"], m["name"], m["race"], m["chr_model"], ", the models of %s" % m["alias_of"] if m["alias_of"] else ""), ""]
        for n in m["notes"]:
            lines.append("- " + n)
        if m["notes"]:
            lines.append("")
        lines += ["| Option | Category | Shadowlands offers | Creator | Mechanism | Greyed | Drawn | Gaps: what, the rule that left it, what would draw it |", "|---|---|---|---|---|---|---|---|"]
        for r in m["options"]:
            c = r.get("creator")
            creator = "-" if not c else "%d%s" % (c["choices"], " (%d a death knight's)" % c["dk"] if c.get("dk") else "")
            if c and r.get("choices", {}).get("extra"):
                creator += " (+%s)" % r["choices"].get("extra_words", "")
            gaps = " / ".join("**%s**: %s. Rule: %s. %s" % (i["code"], i["text"], i["rule"], ("Would draw it: %s." % i["fix"]) if i.get("fix") else "") for i in r["issues"])
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (r["name"], r["category"], choice_words(r), creator, r.get("mechanism_words", ""),
                                                                  r.get("greyed", ""), STATUS_WORDS.get(r.get("drawn"), ""), gaps or r.get("note", "")))
        if m["forms"]:
            lines += ["", "Druid forms (not a character's looks in 3.3.5: fixed creatures; not counted): " +
                      ", ".join("%s (%d choices)" % (f["name"], f["sl"].get("rows", 0)) for f in m["forms"])]
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv):
    if len(argv) == 6 and argv[1] == "geosets":
        looks = sl_looks.load_looks(argv[2])
        races = json.load(open(argv[3]))
        out = geosets_of(looks, races, argv[4])
        with open(argv[5], "w") as f:
            json.dump(out, f, sort_keys=True)
        print("%d models" % len(out))
        return 0
    if len(argv) >= 7 and argv[1] == "report":
        opts = argv[7:]
        geosets = json.load(open(opts[opts.index("--geosets") + 1])) if "--geosets" in opts else None
        package = opts[opts.index("--package") + 1] if "--package" in opts else None
        looks = sl_looks.load_looks(argv[3])
        races = json.load(open(argv[4]))
        cov = build(argv[2], looks, races, geosets, package)
        with open(argv[5], "w") as f:
            json.dump(cov, f, indent=1, sort_keys=True)
        with open(argv[6], "w", encoding="utf-8") as f:
            f.write(markdown(cov))
        totals = collections.Counter(r["drawn"] for m in cov["models"].values() for r in m["options"])
        print("%d models; options drawn %d, but for the native mod's part %d, partly %d, not %d" % (
            len(cov["models"]), totals["yes"], totals["native"], totals["partly"], totals["no"]))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
