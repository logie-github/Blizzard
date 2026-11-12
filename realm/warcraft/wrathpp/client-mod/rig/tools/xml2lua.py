#!/usr/bin/env python3
"""A glue XML file (the game's own, or a module's) as a Lua table the rig's engine builds frames from:
    xml2lua.py FILE.xml OUT.lua      -> return { tag = "Ui", attr = {}, text = "...", [1] = child, ... }"""
import re, sys
import xml.etree.ElementTree as ET

def q(text):
    return '"' + text.replace('\\', '\\\\').replace('"', '\\"').replace('\r', '').replace('\n', '\\n') + '"'

def lua(e, depth=0):
    tag = e.tag.split('}')[-1]
    pad = '\t' * depth
    parts = ['tag = %s' % q(tag)]
    if e.attrib:
        parts.append('attr = { ' + ', '.join('[%s] = %s' % (q(k), q(v)) for k, v in e.attrib.items()) + ' }')
    text = (e.text or '').strip()
    if text:
        parts.append('text = %s' % q(e.text))
    kids = [lua(c, depth + 1) for c in e if isinstance(c.tag, str)]
    if not kids:
        return '{ ' + ', '.join(parts) + ' }'
    return '{ ' + ', '.join(parts) + ',\n' + ''.join('%s\t%s,\n' % (pad, k) for k in kids) + pad + '}'

src = open(sys.argv[1], encoding='utf-8', errors='replace').read().replace('\r', '')
src = src.lstrip('\ufeff')
root = ET.fromstring(src)
open(sys.argv[2], 'w', encoding='utf-8').write('return ' + lua(root) + '\n')
print(sys.argv[1].split('/')[-1], sum(1 for _ in root.iter()), 'elements')
