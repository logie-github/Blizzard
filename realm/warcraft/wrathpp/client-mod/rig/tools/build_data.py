#!/usr/bin/env python3
"""The game's tables the creation screen works from, as text the rig's Lua reads:
    build_data.py DBC_DIR CLIENT_CHARSECTIONS CLIENT_FACIALHAIR OUT_DIR
DBC_DIR: the stock 3.3.5a tables (ChrRaces, ChrClasses, CharBaseInfo, FactionTemplate, FactionGroup, CharStartOutfit);
the two CLIENT_ files: the game's character tables as the phone has them (the looks, the undead skins)."""
import os, struct, sys

def table(path):
    d = open(path, 'rb').read()
    magic, n, fields, size, ssz = struct.unpack_from('<4s4I', d, 0)
    assert magic == b'WDBC', path
    return n, fields, size, d[20:20 + n * size], d[20 + n * size:]

def ints(path):
    n, fields, size, body, strs = table(path)
    return [struct.unpack_from('<%di' % (size // 4), body, i * size) for i in range(n)], strs

def s(strs, off):
    return strs[off:strs.index(b'\0', off)].decode('utf-8', 'replace')

def q(text):
    return '"' + text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'

dbc, sections, facial, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
rows, _ = ints(sections)
with open(os.path.join(out, 'charsections.txt'), 'w') as f:
    for r in rows:                                  # id race sex section tex1 tex2 tex3 flags variation colour
        f.write('%d %d %d %d %d %d\n' % (r[1], r[2], r[3], r[7], r[8], r[9]))
rows, _ = ints(facial)
with open(os.path.join(out, 'facialhair.txt'), 'w') as f:
    for r in rows:
        f.write('%d %d %d\n' % (r[0], r[1], r[2]))
L = ['-- made by rig/tools/build_data.py from the game tables', 'return {']
groups, gs = ints(os.path.join(dbc, 'FactionGroup.dbc'))
templates, _ = ints(os.path.join(dbc, 'FactionTemplate.dbc'))
tmpl = {t[0]: t for t in templates}
races, rs = ints(os.path.join(dbc, 'ChrRaces.dbc'))
L.append('\tfactionGroups = {')
for g in groups:
    L.append('\t\t{ mask = %d, internal = %s, name = %s },' % (g[1], q(s(gs, g[2])), q(s(gs, g[3]))))
L.append('\t},')
L.append('\traces = {            -- in the table\'s own order')
for r in races:
    t = tmpl.get(r[2])
    L.append('\t\t{ id = %d, flags = %d, factionGroup = %s, prefix = %s, file = %s, name = %s, nameFemale = %s, nameMale = %s, facial = { %s, %s }, hair = %s, expansion = %d },' % (
        r[0], r[1], t[3] if t else 'nil', q(s(rs, r[6])), q(s(rs, r[11])), q(s(rs, r[14])), q(s(rs, r[31])), q(s(rs, r[48])), q(s(rs, r[65])), q(s(rs, r[66])), q(s(rs, r[67])), r[68]))
L.append('\t},')
classes, cs = ints(os.path.join(dbc, 'ChrClasses.dbc'))
L.append('\tclasses = {')
for c in classes:
    L.append('\t\t{ id = %d, name = %s, nameFemale = %s, nameMale = %s, file = %s, expansion = %d },' % (c[0], q(s(cs, c[4])), q(s(cs, c[21])), q(s(cs, c[38])), q(s(cs, c[55])), c[59]))
L.append('\t},')
n, fields, size, body, _ = table(os.path.join(dbc, 'CharBaseInfo.dbc'))
L.append('\tbaseInfo = { ' + ', '.join('{ %d, %d }' % (body[i * size], body[i * size + 1]) for i in range(n)) + ' },')
L.append('}')
open(os.path.join(out, 'tables.lua'), 'w').write('\n'.join(L) + '\n')
print('written', out, len(races), 'races', len(classes), 'classes', n, 'race-class pairs')
