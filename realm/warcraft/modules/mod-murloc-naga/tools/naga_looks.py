# SPDX-License-Identifier: GPL-3.0-or-later
"""The naga's headdresses and outfits: what the character creation screen offers and what each choice
is made of, read by tools/naga_parts.py (the parts and textures, from the game's files as the server is
packaged) and tools/build_data.py (the tables). Data only.

Blizzard's own, made for the naga's body (Battle for Azeroth's Nazjatar naga wear them: the files end
_na_m and _na_f):
  - Headdress (the hair style, ChrRaces' token NAGA): none, and for men the myrmidon's crown and the
    warlord's helm, for women the sea witch's headdress: geosets 2, 3... of group 0;
  - Headdress color (the hair colour): the headdress's colours (its item displays' textures, the hair
    row's texture: the model's type 6);
  - Features: none (geoset 101, which the model hasn't), and each outfit in each of its colours:
    geosets 102, 103... of group 1.
"""

# The parts: (model file id, [its colours' texture file ids], name).
HEADDRESSES = {
    "Male": [(2918380, [2918410, 2918411, 2918412], "Crown"), (2923922, [2925124, 2925125, 2925126, 2925127], "Helm")],
    "Female": [(2923920, [2924704, 2924705, 2924707, 2924708], "Headdress")],
}
OUTFITS = {
    "Male": [(2918378, [2918404, 2918405, 2918406], "Harness"), (2923915, [2960123, 2960124, 2960125, 2960126], "Plate")],
    "Female": [(2923909, [2924696, 2924697, 2924698, 2924699], "Regalia")],
}


def colours(sex):
    """How many headdress colours a sex has (the most of its headdresses'; one with fewer repeats its first)."""
    return max(len(t) for _, t, _ in HEADDRESSES[sex])


def features(sex):
    """The features after none, in order: (outfit index, its colour)."""
    return [(o, c) for o, (_, textures, _) in enumerate(OUTFITS[sex]) for c in range(len(textures))]


def headdress_texture(sex, style, colour):
    """The hair row's texture of a headdress style (1...) and colour (none for style 0)."""
    if style == 0:
        return ""
    return "Character\\Naga_\\%s\\Naga%s%s%d.blp" % (sex, sex, HEADDRESSES[sex][style - 1][2], colour)


def hair_geoset(style):
    return 0 if style == 0 else style + 1          # (group 0: none 0, as the game's own bald styles)


def feature_geoset(style):
    # Group 1: mesh 100 + this. The game reads a facial style's geoset 0 as "leave the group as it is"
    # (every outfit shown at once), so none is 1, a mesh the naga hasn't.
    return style + 1
