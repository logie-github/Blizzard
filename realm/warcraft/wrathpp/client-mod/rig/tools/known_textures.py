#!/usr/bin/env python3
"""The texture files the 3.3.5 client is known to have, for the rig's check of what the creator names:
    known_textures.py STOCK_DIR DBC_DIR LIST OUT.lua
STOCK_DIR: the phone's own glue files (every Interface\\... file they name is one the game has);
DBC_DIR:   the game's tables: an icon an item (ItemDisplayInfo.dbc) or a spell (SpellIcon.dbc) of 3.3.5 has is in the client;
LIST:      textures335.txt, the files 3.3.5's own in-game interface names.
OUT.lua returns a set of the names in small letters, with \\ between folders and without .blp."""
import glob, os, re, struct, sys

stock, dbc, listed, out = sys.argv[1:5]
known = set()

def add(name):
    name = name.strip().replace('/', '\\').lower()
    name = re.sub(r'\\+', r'\\', name)
    name = re.sub(r'\.(blp|tga)$', '', name)
    if name.startswith('interface\\'):
        known.add(name)

for path in glob.glob(os.path.join(stock, '*')):
    if not path.lower().endswith(('.xml', '.lua')):
        continue
    src = open(path, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r'Interface(?:\\\\?[A-Za-z0-9_ .-]+)+', src):
        add(m.group(0))

def table(path):
    d = open(path, 'rb').read()
    magic, n, fields, size, ssz = struct.unpack_from('<4s4I', d, 0)
    assert magic == b'WDBC', path
    return n, size, d[20:20 + n * size], d[20 + n * size:]

def text(strs, off):
    return strs[off:strs.index(b'\0', off)].decode('utf-8', 'replace')

icons = 0
# ItemDisplayInfo: id, model 2, model's texture 2, icon 2, ...: the icon's name without its folder
n, size, body, strs = table(os.path.join(dbc, 'ItemDisplayInfo.dbc'))
for i in range(n):
    for off in struct.unpack_from('<2I', body, i * size + 5 * 4):
        if off:
            add('Interface\\Icons\\' + text(strs, off)); icons += 1
# SpellIcon: id, the icon's whole name
n, size, body, strs = table(os.path.join(dbc, 'SpellIcon.dbc'))
for i in range(n):
    off = struct.unpack_from('<I', body, i * size + 4)[0]
    if off:
        add(text(strs, off)); icons += 1

for line in open(listed, encoding='utf-8'):
    line = line.split('#')[0].strip()
    if line:
        add(line.split('\t')[0])

with open(out, 'w', encoding='utf-8') as f:
    f.write('return {\n')
    for name in sorted(known):
        f.write('\t["%s"] = true,\n' % name.replace('\\', '\\\\'))
    f.write('}\n')
print('%d texture names the client is known to have (%d from the items and spells)' % (len(known), icons))
