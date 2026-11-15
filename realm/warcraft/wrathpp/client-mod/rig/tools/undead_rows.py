#!/usr/bin/env python3
"""The game's character table with undead skins in it as the app's import puts them (WrathppUndead.kt: K new colours
after each race and sex's own, each with a skin row, an underwear row and a face row for every face number, at the
table's end), and the creator's file of them (WrathppUndead.lua), for the rig:
    undead_rows.py CharSections.dbc OUT.dbc OUT.lua [K]
The races and sexes the undead pack has: nine races' men and women but the Forsaken's and the Blood Elf man."""
import struct, sys

src, out, lua = sys.argv[1:4]
K = int(sys.argv[4]) if len(sys.argv) > 4 else 4
NAMES = ["Rot Green", "Grave Blue", "Ashen", "Dusk Violet", "Bone", "Frost"]
d = open(src, "rb").read()
magic, n, fields, size, ssz = struct.unpack_from("<4s4I", d, 0)
assert magic == b"WDBC" and fields == 10
rows = [list(struct.unpack_from("<10i", d, 20 + i * size)) for i in range(n)]
strings = bytearray(d[20 + n * size:])
next_id = max(r[0] for r in rows) + 1
# (each skin's texture named as the undead pack names it, …SkinUndead00_NN.blp: what the app's import and the Wrath++
# server (WrathppUndeadStart.cpp) know an undead skin by)
RACE_FOLDERS = {1: "Human", 2: "Orc", 3: "Dwarf", 4: "NightElf", 6: "Tauren", 7: "Gnome", 8: "Troll", 10: "BloodElf", 11: "Draenei"}
def name_of(race, sex, k):
    folder = "Character\\%s\\%s\\%s%s" % (RACE_FOLDERS[race], ("Male", "Female")[sex], RACE_FOLDERS[race], ("Male", "Female")[sex])
    at = len(strings)
    strings.extend(("%sSkinUndead00_%02d.blp" % (folder, k)).encode() + b"\0")
    return at
first = {}
for race in (1, 2, 3, 4, 6, 7, 8, 10, 11):
    for sex in (0, 1):
        if (race, sex) == (10, 0):
            continue
        mine = [r for r in rows if r[1] == race and r[2] == sex]
        skins = [r for r in mine if r[3] == 0]
        if not skins:
            continue
        living = max(r[9] for r in skins) + 1
        first_skin = next(r for r in skins if r[9] == 0)
        underwear = next((r for r in mine if r[3] == 4 and r[9] == 0), None)
        faces = [r for r in mine if r[3] == 1 and r[9] == 0]
        first[(race, sex)] = living
        for k in range(K):
            colour = living + k
            rows.append([next_id, race, sex, 0, name_of(race, sex, k), 0, 0, first_skin[7], 0, colour]); next_id += 1
            rows.append([next_id, race, sex, 4, 0, 0, 0, (underwear or first_skin)[7], 0, colour]); next_id += 1
            for f in faces:
                rows.append([next_id, race, sex, 1, 0, 0, 0, f[7], f[8], colour]); next_id += 1
body = b"".join(struct.pack("<10i", *r) for r in rows)
open(out, "wb").write(struct.pack("<4s4I", b"WDBC", len(rows), 10, 40, len(strings)) + body + bytes(strings))
with open(lua, "w") as f:
    f.write("-- Wrath++'s undead skins as the app's import writes them (the rig's: tools/undead_rows.py).\nWrathppUndead = { models = {\n")
    for (race, sex), living in sorted(first.items()):
        skins = ", ".join('{ n = "%s", s = %d }' % (NAMES[k % len(NAMES)], 0x607060 + 0x101010 * k) for k in range(K))
        f.write('\t["%d_%d"] = { first = %d, skins = { %s } },\n' % (race, sex, living, skins))
    f.write("} }\n")
print("undead skins:", K, "for", len(first), "races and sexes;", len(rows) - n, "rows added")
