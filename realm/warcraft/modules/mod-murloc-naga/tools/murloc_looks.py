# SPDX-License-Identifier: GPL-3.0-or-later
"""The murlocs' looks: what the character creation screen offers and what each choice is made of,
read by tools/murloc_model.py (the model and textures, from the game's files as the server is
packaged) and tools/build_data.py (the tables). Data only.

The model is Blizzard's newer murloc (creature/murloc2/murloc2.m2, file 1113034: the murlocs of
Cataclysm and after), made a character's. Its fins (the spines of its crest and back) are cut from
its body and drawn with the character's hair texture, so they take their own colour; its kin built
on the same skeleton (every bone of theirs at one of its bones' places, a few added) lend parts: the
classic murloc's crest (the murlocs of 2004), the deep sea murloc's sail, the shark-hooded murloc's outfit, Maria's hair
and dress (the murloc in a dress of the Darkmoon Faire), the demon hunter murloc's horns, blindfold
and loincloth, the deep sea murloc's lure.

The screen's choices (its labels set by data/client/Interface/GlueXML/MurlocNagaCreate.lua):
  - Skin Color: the body in each skin the game gives murloc2 and its re-skinned kin (13);
  - Eye Color (the game's Face): the eyes of each of those skins, and a few made from them;
  - Fins (the game's Hair Style): the crest as it is, short, long, swept back, the classic
    murloc's crest and the deep sea murloc's sail; each a geoset of group 0 (CharHairGeosets);
  - Fin Color (the game's Hair Color): the fins of each skin, and a few made from them;
  - Features (the game's Facial Hair): none, the demon horns, the lure, the blindfold, the shark
    outfit, the loincloth (and for women Maria's hair, and her dress with it); each a geoset of group 1
    (CharacterFacialHairStyles).

How the 3.3.5 game draws a character decides where each goes. The body and eyes are drawn with the
character's composed texture, in its face region (FaceUpper and FaceLower, 256 x 192 at the HD
looks' 512 scale): the only part of it no armour is drawn into, so a murloc's chest piece or boots
don't paint its scales. A face row (CharSections type 1: its eye colour and the skin colour) names
both of that region's textures: FaceLower, the body's lower part (a skin colour's); FaceUpper, the
eyes beside the body's upper part (an eye colour's and a skin colour's).
"""

BASE_MODEL = 1113034                 # creature/murloc2/murloc2.m2
# Its emotes (talk, point, cheer, bow, cry...: murloc2 has none) are the murloc costume's
# (creature/murloccostume/murloccostume_noflag.m2, BlizzCon 2007's: tools/murloc_anims.py).
COSTUME_MODEL = 125044

# Skin colours (file ids of the textures the game's displays of murloc2 and its re-skinned kin give it).
SKINS = [
    (1113060, "Grey"), (1113057, "Blue"), (1113058, "Green"), (1113061, "Pale"), (1113059, "Orange"),
    (1450941, "Gold"), (1589499, "Fel"), (2764576, "Red"), (3492077, "Purple"), (1115036, "Slate"),
    (3987167, "Abyssal"), (4693215, "Bronze"), (4693216, "Ice"),
]
# The eyes' place in those textures (u0, v0, u1, v1): where murloc2's eye mesh reads them.
EYES = (0.015, 0.355, 0.135, 0.475)
# The skin whose fins are the fins' texture's shape (the one whose fins are cut by their colour).
FIN_SKIN = 1                         # Blue: its fins gold, its body blue
# Fin texels in that skin: hue (0 to 1) between these, saturation and lightness above these.
FIN_HUE, FIN_SATURATION, FIN_LIGHTNESS = (0.07, 0.2), 0.4, 0.25

# Eye colours: (name, the skin whose eyes, hue (0 to 1; -1 kept), saturation x, lightness x).
EYE_COLOURS = [
    ("Silver", 0, -1, 1, 1), ("Sky", 1, -1, 1, 1), ("Jade", 2, -1, 1, 1), ("Pearl", 3, -1, 1, 1),
    ("Amber", 4, -1, 1, 1), ("Gold", 5, -1, 1, 1), ("Fel", 6, -1, 1, 1), ("Blood", 7, -1, 1, 1),
    ("Violet", 8, -1, 1, 1), ("Lilac", 9, -1, 1, 1), ("Abyssal", 10, -1, 1, 1), ("Ember", 11, -1, 1, 1),
    ("Frost", 12, -1, 1, 1), ("Onyx", 0, -1, 0.4, 0.35), ("Rose", 1, 0.93, 1.0, 1.0), ("Sea Green", 1, 0.42, 1.0, 0.95),
]

# Fin colours: (name, the skin whose fins, hue (-1 kept), saturation x, lightness x).
FIN_COLOURS = [
    ("Gold", 1, -1, 1, 1), ("Crimson", 2, -1, 1, 1), ("Plum", 0, -1, 1, 1), ("Amethyst", 4, -1, 1, 1),
    ("Rust", 5, -1, 1, 1), ("Fel", 6, -1, 1, 1), ("Olive", 7, -1, 1, 1), ("Teal", 8, -1, 1, 1),
    ("Abyssal", 10, -1, 1, 1), ("Sand", 11, -1, 1, 1), ("Frost", 12, -1, 1, 1),
    ("Coral", 1, 0.98, 1.0, 1.15), ("Sea Green", 1, 0.42, 0.9, 1.0), ("Azure", 1, 0.58, 1.0, 1.1),
    ("Ebony", 0, -1, 0.5, 0.45), ("Bone", 11, -1, 0.35, 1.25),
]

# The fins' textures' size (the hair rows': each the whole of the skin it's from, scaled).
FIN_SIZE = 256

# Fin styles (the hair styles), each (name, how): "own" murloc2's fins, each spine made [scale] times
# as long from its root on the body and swept [sweep] degrees back; "from" another model's fins: the
# pieces of [batch] reaching above [z] (yards above the feet), its texture [texture] recoloured to the
# fin colour.
FIN_STYLES = [
    ("Crest", {"own": True, "scale": 1.0, "sweep": 0}),
    ("Short crest", {"own": True, "scale": 0.5, "sweep": 0}),
    ("Long crest", {"own": True, "scale": 1.45, "sweep": 0}),
    ("Swept crest", {"own": True, "scale": 1.15, "sweep": 55}),
    ("Classic crest", {"model": 125024, "batch": 1, "z": 1.1, "texture": 125036, "name": "Classic"}),
    ("Deep sea sail", {"model": 360359, "batch": 2, "z": 0.6, "texture": 360360, "name": "Sail"}),
]

# The parts, from the models that lend them: [model] (file id), [batch] (its skin's batch, in order),
# [texture] (file id), and which of the batch's pieces (connected parts of its mesh) are the part:
#   "top"        pieces reaching above z (yards above the feet),
#   "below"      pieces not reaching above z,
#   "head"       triangles on the head's bones alone,
#   "body"       the rest,
#   "centre"     pieces whose centre is in the box (x0, x1, y0, y1, z0, z1),
#   "added"      triangles on the bones murloc2 hasn't (the lure's own) with their centre in the box.
PARTS = {
    "Outfit":    {"model": 1502337, "batch": 1, "texture": 1502344, "take": ("below", 1.2)},
    "Hair":      {"model": 1502336, "batch": 1, "texture": 1502339, "take": ("head",)},
    "Dress":     {"model": 1502336, "batch": 1, "texture": 1502339, "take": ("body",)},
    "Horns":     {"model": 1129417, "batch": 0, "texture": 1131231, "take": ("centre", -1, 1, 0.15, 1, 1.0, 2)},
    "HornsL":    {"model": 1129417, "batch": 0, "texture": 1131231, "take": ("centre", -1, 1, -1, -0.15, 1.0, 2)},
    "Blindfold": {"model": 1129417, "batch": 0, "texture": 1131231, "take": ("centre", 0.2, 0.5, -0.05, 0.05, 0.75, 1.0)},
    "Loincloth": {"model": 1129417, "batch": 0, "texture": 1131231, "take": ("centre", -0.2, 0.2, -0.05, 0.05, 0.3, 0.62)},
    "Lure":      {"model": 360359, "batch": 0, "texture": 360360, "take": ("added", 0.15, 1.0, -0.3, 0.3, 1.05, 2)},
    "LureBulb":  {"model": 360359, "batch": 1, "texture": 360360, "take": ("top", 1.4)},
}

# Features (the facial hair styles), a sex's: (name, its parts); the first, none.
FEATURES = {
    "Male": [("None", []), ("Demon horns", ["Horns", "HornsL"]), ("Lure", ["Lure", "LureBulb"]),
             ("Blindfold", ["Blindfold"]), ("Shark outfit", ["Outfit"]), ("Loincloth", ["Loincloth"])],
    "Female": [("None", []), ("Maria's hair", ["Hair"]), ("Demon horns", ["Horns", "HornsL"]),
               ("Lure", ["Lure", "LureBulb"]), ("Blindfold", ["Blindfold"]), ("Maria's dress", ["Hair", "Dress"]),
               ("Shark outfit", ["Outfit"]), ("Loincloth", ["Loincloth"])],
}

# The parts' textures' names (Character\\Murloc\\Murloc<name>.blp), by file id.
TEXTURE_NAMES = {1502344: "Shark", 1502339: "Maria", 1131231: "Demon", 360360: "DeepSea"}


# The geosets the choices show. The game reads a style's geoset 0 as "leave the group as it is" (every
# one of its meshes shown: a murloc in every outfit at once), so none is 1, a mesh the model hasn't.
def fin_geoset(style):
    return style + 2                 # group 0: 2, 3...


def feature_geoset(feature):
    return feature + 1               # group 1: mesh 100 + this (none: 101, which isn't)


# The composed texture's face region (pixels at the 512 scale): the eyes' block, and the body's.
COMPOSED = 512
FACE_UPPER = (0, 320, 256, 384)
FACE_LOWER = (0, 384, 256, 512)
EYE_BLOCK = (0, 320, 64, 384)        # in FaceUpper
BODY_BLOCK = (64, 320, 256, 512)     # FaceUpper's rest and FaceLower's: 192 x 192


def face_lower(skin):
    return "Character\\Murloc\\MurlocBody%02d.blp" % skin


def face_upper(eyes, skin):
    return "Character\\Murloc\\MurlocEyes%02d_%02d.blp" % (eyes, skin)


def fin_texture(style, colour):
    how = FIN_STYLES[style][1]
    return "Character\\Murloc\\MurlocFins%s%02d.blp" % ("" if how.get("own") else how["name"], colour)
