"""Each body preset written into the refined model's vertices: the viewer's reshaped rest positions and fitted texture
coordinates for the vertices it draws; a vertex of another piece at the same place (within 3 mm, facing alike) moved
with it; normals turned by how much the shape turned the surface. usage: presets.py RACE MODEL_DIR EXPORT_DIR DATA OUT"""
import json, base64, os, sys, struct, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refine
from scipy.spatial import cKDTree
race, mdir, edir, data, out = sys.argv[1:6]
src = '%s/Character/%s/Female/%sFemale' % (mdir, race, race)
m2b = open(src + '.m2', 'rb').read(); skb = open(src + '00.skin', 'rb').read()
nv, ov = struct.unpack_from('<II', m2b, 60)
rec = np.frombuffer(m2b, np.uint8, nv * 48, ov).reshape(nv, 48).copy()
P0 = rec[:, 0:12].copy().view('<f4').reshape(nv, 3).astype(np.float64)
N0 = rec[:, 20:32].copy().view('<f4').reshape(nv, 3).astype(np.float64)
UV0 = rec[:, 32:40].copy().view('<f4').reshape(nv, 2).astype(np.float64)
d = json.load(open(data)); mv = np.frombuffer(base64.b64decode(d['mv']), np.uint32).astype(np.int64)
v, ix, pp, secs, bt, bn, mx = refine.read_skin(skb)
tris = np.concatenate([v[ix[s[4] + s[1] * 65536: s[4] + s[1] * 65536 + s[5]]].reshape(-1, 3) for s in secs])
f = lambda s: np.frombuffer(base64.b64decode(s), np.float32).astype(np.float64)
key = np.round(P0, 5); _, weld = np.unique(key, axis=0, return_inverse=True); weld = weld.ravel()
def vnormals(P):
    fn = np.cross(P[tris[:, 1]] - P[tris[:, 0]], P[tris[:, 2]] - P[tris[:, 0]])
    acc = np.zeros((weld.max() + 1, 3))
    for j in range(3): np.add.at(acc, weld[tris[:, j]], fn)
    n = acc[weld]; return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
G0 = vnormals(P0)
summary = {}
for pr in ('Petite', 'Curvy', 'Voluptuous'):
    e = json.load(open('%s/%s_%s.json' % (edir, race, pr)))
    X = f(e['rest']).reshape(-1, 3); U = f(e['uv']).reshape(-1, 2)
    assert np.abs(f(e['P']).reshape(-1, 3) - P0[mv]).max() < 1e-5
    P = P0.copy(); P[mv] = X
    D = np.zeros((nv, 3)); D[mv] = X - P0[mv]
    # other pieces at the same places (a robe's edge on the body, a bare piece's twin) moved alike
    drawn = np.zeros(nv, bool); drawn[mv] = True
    tree = cKDTree(P0[mv]); others = np.where(~drawn)[0]
    dist, j = tree.query(P0[others])
    near = (dist < 0.003) & (np.einsum('ij,ij->i', N0[others], N0[mv[j]]) > 0.3)
    P[others[near]] = P0[others[near]] + D[mv[j[near]]]
    UVn = UV0.copy(); ch = np.abs(U - UV0[mv]).max(1) > 1e-6; UVn[mv[ch]] = U[ch]
    G = vnormals(P)
    moved = np.linalg.norm(P - P0, axis=1) > 1e-6
    Nn = N0.copy(); Nn[moved] = N0[moved] + G[moved] - G0[moved]
    Nn[moved] /= np.linalg.norm(Nn[moved], axis=1, keepdims=True) + 1e-12
    r = rec.copy()
    r[:, 0:12] = P.astype('<f4').view(np.uint8).reshape(nv, 12)
    r[:, 20:32] = Nn.astype('<f4').view(np.uint8).reshape(nv, 12)
    r[:, 32:40] = UVn.astype('<f4').view(np.uint8).reshape(nv, 8)
    m = bytearray(m2b); m[ov:ov + nv * 48] = r.tobytes()
    dst = '%s/%s/Character/%s/Female/' % (out, pr, race); os.makedirs(dst, exist_ok=True)
    open(dst + '%sFemale.m2' % race, 'wb').write(bytes(m)); open(dst + '%sFemale00.skin' % race, 'wb').write(skb)
    for fn_ in os.listdir(os.path.dirname(src)):
        if fn_.endswith('.anim') and not os.path.exists(dst + fn_): os.symlink(os.path.realpath(os.path.join(os.path.dirname(src), fn_)), dst + fn_)
    summary[pr] = {'moved': int(moved.sum()), 'others_moved': int(near.sum()), 'uv': int(ch.sum()), 'max_mm': float(np.linalg.norm(P - P0, axis=1).max() * 1000)}
print(json.dumps(summary))
