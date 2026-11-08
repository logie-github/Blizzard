#!/usr/bin/env python3
"""The character creation screen's tables checked for every look it can step to: a client's tables
as the game reads them (every patch in), each race and sex with player looks, each slider.

    python3 tools/check_looks.py DBC_DIR

DBC_DIR: CharSections, CharHairGeosets, CharacterFacialHairStyles, ChrRaces, CreatureDisplayInfo
and CreatureModelData (.dbc) out of the client's patch chain. The screen counts a slider's
choices from the rows it finds and then looks up the row for the choice and the skin colour; a
choice with no row for one colour is what crashed it (crash report #34: skins with
the player faces of their race but not the death knights'). So, for each race and sex with player looks (the player's rows, flag 1), as the game's own tables
are laid out (a death knight's skins, flag 4 with 1, carry the death knights' faces alone; the
colours between are the NPCs'):

  * every player skin colour that isn't a death knight's has the same faces as the others, and
    every death knight's skin the same as the other death knights';
  * every player skin colour has its underwear where the race has any;
  * the table is in the game's order: each race, sex, section and variation one run of rows (the
    game builds its look-up from the runs: crash reports #34 to #54);
  * no skin colour below the highest has no row at all (an NPC's will do, as the game's own are):
    the screen reads a colour's row by its number as the race changes;
  * every hair style has the same hair colours, and its row in CharHairGeosets;
  * every facial hair texture style has the same colours;
  * CharacterFacialHairStyles has the features 0 to n-1, each once (a creature race's rows left at a
    player race's number count as its features too);
  * the race's two looks (ChrRaces) have their display and model rows.

Prints each problem and exits 1 if there is one.
"""
import collections
import os
import struct
import sys

PLAYER, DEATH_KNIGHT = 0x1, 0x4


def dbc(path):
    with open(path, "rb") as f:
        d = f.read()
    if d[:4] != b"WDBC":
        raise ValueError("not a DBC: " + path)
    n, fields, size, strings = struct.unpack_from("<4I", d, 4)
    return [struct.unpack_from("<%dI" % fields, d, 20 + i * size) for i in range(n)]


def gaps(values):
    """The choices missing below the highest (the screen counts them from 0)."""
    values = set(values)
    return sorted(set(range(max(values) + 1)) - values) if values else []


def check(folder):
    problems = []
    table = lambda name: dbc(os.path.join(folder, name + ".dbc"))
    sections = table("CharSections")
    hair_geosets = {(r[1], r[2], r[3]) for r in table("CharHairGeosets")}
    facial = collections.defaultdict(set)
    facial_rows = collections.Counter()
    for r in table("CharacterFacialHairStyles"):
        facial[(r[0], r[1])].add(r[2])
        facial_rows[(r[0], r[1], r[2])] += 1
    displays = {r[0]: r for r in table("CreatureDisplayInfo")}
    models = {r[0] for r in table("CreatureModelData")}
    races = {r[0]: r for r in table("ChrRaces")}

    all_colours = collections.defaultdict(set)      # (race, sex) -> skin colours of any row, an NPC's too
    for r in sections:
        if r[3] == 0:
            all_colours[(r[1], r[2])].add(r[9])
    # the game's order: each race, sex, section and variation one run of rows (the game sizes its
    # look-up arrays from the runs; a group split across the table crashed the creation screen)
    seen, previous = set(), None
    for r in sections:
        key = (r[1], r[2], r[3], r[8])
        if key != previous and key in seen:
            problems.append("race %d sex %d: section %d variation %d is split across the table (the game reads only its last run)" % key)
        seen.add(key)
        previous = key
    rows = collections.defaultdict(list)            # (race, sex) -> (section, variation, colour, flags)
    for r in sections:
        if r[7] & PLAYER:
            rows[(r[1], r[2])].append((r[3], r[8], r[9], r[7]))
    looked = 0
    for (race, sex), found in sorted(rows.items()):
        who = "race %d sex %d" % (race, sex)
        skins = {}                                   # colour -> a death knight's
        faces = collections.defaultdict(set)         # colour -> faces
        under = set()
        hair = collections.defaultdict(set)          # style -> colours
        beard = collections.defaultdict(set)
        for section, variation, colour, flags in found:
            if section == 0:
                skins[colour] = bool(flags & DEATH_KNIGHT)
            elif section == 1:
                faces[colour].add(variation)
            elif section == 2:
                beard[variation].add(colour)
            elif section == 3:
                hair[variation].add(colour)
            elif section == 4:
                under.add(colour)
        if not skins or race not in races:
            continue
        looked += 1
        for c in range(max(all_colours[(race, sex)])):
            if c not in all_colours[(race, sex)]:
                problems.append("%s: skin colour %d has no row at all (below its highest, %d)" % (who, c, max(all_colours[(race, sex)])))
        for dk in (False, True):
            group = sorted(c for c, d in skins.items() if d == dk)
            if not group:
                continue
            union = set().union(*(faces[c] for c in group))
            kind = "death knight skin" if dk else "skin"
            if not union:
                problems.append("%s: no faces for its %ss" % (who, kind))
            for c in group:
                if faces[c] != union:
                    problems.append("%s: %s colour %d lacks faces %s (of %d)" % (who, kind, c, sorted(union - faces[c])[:8], len(union)))
        if under:
            for c in sorted(set(skins) - under):
                problems.append("%s: skin colour %d has no underwear" % (who, c))
        if hair:
            colours = set().union(*hair.values())
            for style, cs in sorted(hair.items()):
                if cs != colours:
                    problems.append("%s: hair style %d lacks colours %s" % (who, style, sorted(colours - cs)[:8]))
                if (race, sex, style) not in hair_geosets:
                    problems.append("%s: hair style %d has no CharHairGeosets row" % (who, style))
        if beard:
            colours = set().union(*beard.values())
            for style, cs in sorted(beard.items()):
                if cs != colours:
                    problems.append("%s: facial hair %d lacks colours %s" % (who, style, sorted(colours - cs)[:8]))
        for missing in gaps(facial.get((race, sex), set())):
            problems.append("%s: no feature %d in CharacterFacialHairStyles" % (who, missing))
        for feature in sorted(facial.get((race, sex), set())):
            if facial_rows[(race, sex, feature)] > 1:
                problems.append("%s: feature %d is in CharacterFacialHairStyles %d times" % (who, feature, facial_rows[(race, sex, feature)]))
        if race in races:
            display = races[race][4 + sex]
            if display not in displays:
                problems.append("%s: its look %d has no CreatureDisplayInfo row" % (who, display))
            elif displays[display][1] not in models:
                problems.append("%s: its look %d's model %d has no CreatureModelData row" % (who, display, displays[display][1]))
    return looked, problems


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    looked, problems = check(sys.argv[1])
    for p in problems:
        print("FAIL " + p)
    print("%d races and sexes checked: %s" % (looked, "%d problems" % len(problems) if problems else "every look has its rows"))
    sys.exit(1 if problems else 0)
