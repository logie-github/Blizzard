"""usage: check.py PACKAGE.zip LOOKS_CLIENT_DIR

Each model the package makes, checked as the 3.3.5 client loads it (the pinned decompilation): every header array
inside the file (M2Init), texture names inside it, the combiner list there when flag 0x8 is set; the skin's arrays
inside it; each section's vertices, indices and bones in range, its first index within 16 bits; each batch's section,
material, textures, coordinates, weights, transforms and combiner in range; the layer's batch and section as meant."""
import sys, struct, json, zipfile, hashlib
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layer
LOOKS = sys.argv[2]
z = zipfile.ZipFile(sys.argv[1]); man = json.loads(z.read('wrathpp-body.json'))
SIZES = {0x08: 1, 0x14: 4, 0x1C: 64, 0x24: 2, 0x2C: 88, 0x34: 2, 0x3C: 48, 0x48: 40, 0x50: 16, 0x58: 20, 0x60: 60, 0x68: 2, 0x70: 4,
         0x78: 2, 0x80: 2, 0x88: 2, 0x90: 2, 0x98: 2, 0xD8: 2, 0xE0: 12, 0xE8: 12, 0xF0: 40, 0xF8: 2, 0x100: 36, 0x108: 156,
         0x110: 100, 0x118: 2, 0x120: 176, 0x128: 476, 0x130: 2}
total = 0
for mo in man['models']:
    base = open(LOOKS + '/' + (mo['model'] if mo['shape'] == 0 else mo['anims_of'] + '.m2'), 'rb').read()
    m = layer.unpatch(base, z.read(mo['patch']['file'])); sk = z.read(mo['skin_file']['file'])
    probs = []
    def need(c, w):
        if not c: probs.append(w)
    flags = struct.unpack_from('<I', m, 0x10)[0]
    need(flags & 8, 'flag 0x8')
    A = {}
    for off, size in SIZES.items():
        if off == 0x130 and not flags & 8: continue
        n, o = struct.unpack_from('<II', m, off); A[off] = (n, o)
        need(o <= len(m) and o + size * n <= len(m), 'array %#x out of the file' % off)
    tex = [struct.unpack_from('<IIII', m, A[0x50][1] + i * 16) for i in range(A[0x50][0])]
    for t in tex: need(t[3] + t[2] <= len(m), 'texture name out of the file')
    need(tex[-1][0] == 11 and tex[-2][0] == 6, 'the last two textures: hair, design')
    nm = m[tex[-1][3]:tex[-1][3] + tex[-1][2]]
    need(nm.endswith(b'WppLayer_0.blp\0') and nm.lower().startswith(mo['model'].rsplit('/', 1)[0].replace('/', '\\').lower().encode()), 'design default name %r' % nm)
    arr = lambda off, fmt: [struct.unpack_from(fmt, m, A[off][1] + i * struct.calcsize(fmt))[0] for i in range(A[off][0])]
    texc, coordc, weightc, transc, boneC, comb = arr(0x80, '<H'), arr(0x88, '<H'), arr(0x90, '<H'), arr(0x98, '<H'), arr(0x78, '<H'), arr(0x130, '<H')
    mats = A[0x70][0]; nverts = A[0x3C][0]; nbones = A[0x2C][0]
    need(comb == [1, 0, 1, 1], 'combiners %s' % comb)
    # skin
    hdr = struct.unpack_from('<11I', sk, 4)
    for k in range(5):
        n, o = hdr[2 * k], hdr[2 * k + 1]; sz = [2, 2, 4, 48, 24][k]
        need(o + n * sz <= len(sk), 'skin array %d out of the file' % k)
    sv = struct.unpack_from('<%dH' % hdr[0], sk, hdr[1]); si = struct.unpack_from('<%dH' % hdr[2], sk, hdr[3])
    props = sk[hdr[5]:hdr[5] + 4 * hdr[4]]
    secs = [struct.unpack_from('<10H7f', sk, hdr[7] + i * 48) for i in range(hdr[6])]
    bats = [struct.unpack_from('<BbHHHHHHHHHHH', sk, hdr[9] + i * 24) for i in range(hdr[8])]
    need(len(si) <= 0xFFFF, '%d indices' % len(si))
    need(all(v < nverts for v in sv), 'skin vertex past the model vertices')
    for k, s in enumerate(secs):
        need(s[2] + s[3] <= len(sv) and s[4] + s[5] <= len(si), 'section %d range' % k)
        need(s[7] + s[6] <= len(boneC), 'section %d bones' % k)
        idx = si[s[4]:s[4] + s[5]]
        need(all(s[2] <= i < s[2] + s[3] for i in idx), 'section %d index outside its vertices' % k)
        for j in range(s[2], s[2] + s[3]):
            w = m[A[0x3C][1] + sv[j] * 48 + 12:A[0x3C][1] + sv[j] * 48 + 16]
            for q in range(4):
                if w[q]:
                    need(q < s[8] and props[4 * j + q] < s[6] and boneC[s[7] + props[4 * j + q]] < nbones, 'section %d vertex %d bone slot %d' % (k, j, q))
    for k, b in enumerate(bats):
        tc = b[8]
        need(b[3] < len(secs) and b[6] < mats, 'batch %d section/material' % k)
        need(b[9] + tc <= len(texc) and all(texc[b[9] + q] < len(tex) for q in range(tc)), 'batch %d textures' % k)
        need(b[10] + tc <= len(coordc) and b[11] + tc <= len(weightc) and b[12] + tc <= len(transc), 'batch %d combos' % k)
        need(b[2] + tc <= len(comb), 'batch %d combiner %d' % (k, b[2]))
        need(b[7] == 0, 'batch %d layered' % k)
    lay = [b for b in bats if secs[b[3]][0] == 1901]
    need(len(lay) == 1 and lay[0][8] == 2 and lay[0][2] == 2 and [tex[texc[lay[0][9]]][0], tex[texc[lay[0][9] + 1]][0]] == [6, 11]
         and coordc[lay[0][10]:lay[0][10] + 2] == [0, 1], 'the layer batch')
    need(sum(1 for s in secs if s[0] == 1901) == 1 and [s for s in secs if s[0] == 1901][0][4] <= 0xFFFF, 'the layer section')
    need(all(b[2] == 0 for b in bats if secs[b[3]][0] != 1901), 'other batches combiner 0')
    print('%-10s shape %d: %d batches, %d sections, %d indices: %s' % (mo['race'], mo['shape'], len(bats), len(secs), len(si), 'ok' if not probs else probs[:5]))
    total += len(probs)
print('problems:', total)
sys.exit(1 if total else 0)
