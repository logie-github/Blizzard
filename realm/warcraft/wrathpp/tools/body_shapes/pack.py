"""The body shapes zip: for each race, the refined skin and each preset's vertex block, named for the looks' model they
were made from (its SHA-256). usage: pack.py OUT.zip LOOKS_CLIENT_DIR GAME_DIR RACE..."""
import hashlib, json, os, struct, sys, zipfile
out, looks, game = sys.argv[1:4]; races = sys.argv[4:]
PRESETS = ['Petite', 'Curvy', 'Voluptuous']
man = {'format': 1, 'kind': 'wrathpp-body', 'presets': PRESETS, 'default': 'Curvy', 'models': []}
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for race in races:
        rel = 'Character/%s/Female/%sFemale' % (race, race)
        base = open('%s/%s.m2' % (looks, rel), 'rb').read()
        entry = {'race': race, 'model': rel + '.m2', 'skin': rel + '00.skin', 'looks_sha256': hashlib.sha256(base).hexdigest(),
                 'looks_vertices': struct.unpack_from('<I', base, 60)[0], 'blocks': {}}
        skin = None
        for pr in PRESETS:
            m = open('%s/%s/%s.m2' % (game, pr, rel), 'rb').read()
            nv, ov = struct.unpack_from('<II', m, 60)
            blk = m[ov:ov + nv * 48]
            name = '%s/%s.vtx' % (race, pr); z.writestr(name, blk)
            entry['blocks'][pr] = {'file': name, 'vertices': nv, 'sha256': hashlib.sha256(blk).hexdigest()}
            sk = open('%s/%s/%s00.skin' % (game, pr, rel), 'rb').read()
            assert skin is None or sk == skin; skin = sk
        z.writestr('%s/%sFemale00.skin' % (race, race), skin)
        entry['skin_file'] = '%s/%sFemale00.skin' % (race, race); entry['skin_sha256'] = hashlib.sha256(skin).hexdigest()
        man['models'].append(entry)
    z.writestr('wrathpp-body.json', json.dumps(man, indent=1))
print(json.dumps(man, indent=1)[:900]); print(os.path.getsize(out) // 1024, 'KB')
