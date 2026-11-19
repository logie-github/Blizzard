"""The Body tab's picture (the Body tab's icon, in the style of the other category icons): a
woman's torso (shoulders, chest, waist, belly with its navel, hips, the thighs' tops) in the relief Shadowlands' category
pictures are in (lit from the top left, edged darker, faintly faceted as their stone is), gold with its glow for the one
chosen and grey for the others, on the Face picture's own ring and disc with its head painted out. The figure is drawn
here, from no file; sl_ui_art.py makes "charactercreate-icon-customize-figure" (and "-selected") of it."""
import numpy as np
from PIL import Image, ImageFilter


def _smooth(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def torso_height(n):
    """[n] x [n]: the figure's height above the disc (0 off it), and its outline (1 on, 0 off; soft at the edge)."""
    v, u = np.mgrid[0:n, 0:n].astype(np.float64) / (n - 1)
    u = (u - 0.5) * 2                                   # -1 .. 1 across
    # half-width down the figure (v 0 at the neck's cut, 1 at the thighs' cut), a woman's: neck, shoulders, the chest's
    # sides, the waist, the hips at their widest, the thighs
    ks = np.array([0.00, 0.06, 0.13, 0.20, 0.30, 0.40, 0.50, 0.58, 0.68, 0.78, 0.88, 1.00])
    ws = np.array([0.20, 0.24, 0.60, 0.66, 0.60, 0.53, 0.44, 0.42, 0.52, 0.62, 0.60, 0.50])
    half = np.interp(v, ks, ws)
    # (a soft curve through the points: the half-width eased between them)
    half = np.array(Image.fromarray((half * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(n / 40))) / 255.0
    inside = half - np.abs(u)
    # the legs: a narrow gap between the thighs from the bottom up to the top of the thighs
    gap = _smooth((v - 0.84) / 0.08) * _smooth((0.06 - np.abs(u)) / 0.04)
    inside -= gap * 0.2
    # the neck's cut and the arms' cuts at the shoulders are rounded off a little
    edge = _smooth(inside / 0.06) * _smooth(v / 0.03) * _smooth((1 - v) / 0.02)
    # height: a rounded body, then the chest, the belly, the hips; a navel and a line under the chest
    body = np.sqrt(np.clip(inside / np.maximum(half, 1e-3), 0, 1)) * 0.55
    h = body.copy()
    for s in (-1, 1):
        bu, bv = 0.30 * s, 0.33
        d = np.sqrt(((u - bu) / 0.27) ** 2 + ((v - bv) / 0.13) ** 2)
        h += 0.62 * np.clip(1 - d, 0, 1) ** 1.3                      # a chest form
    d = np.sqrt((u / 0.36) ** 2 + ((v - 0.66) / 0.16) ** 2); h += 0.18 * np.clip(1 - d, 0, 1) ** 1.5        # the belly
    for s in (-1, 1):
        d = np.sqrt(((u - 0.42 * s) / 0.25) ** 2 + ((v - 0.80) / 0.14) ** 2); h += 0.22 * np.clip(1 - d, 0, 1) ** 1.4   # the hips
    d = np.sqrt((u / 0.035) ** 2 + ((v - 0.62) / 0.03) ** 2); h -= 0.10 * np.clip(1 - d, 0, 1)                       # the navel
    d = np.sqrt((u / 0.04) ** 2 + ((v - 0.47) / 0.10) ** 2); h -= 0.05 * np.clip(1 - d, 0, 1)                        # the line down the middle
    return h * edge, edge


def shade(h, edge, ramp, light=(-0.55, -0.65, 0.52)):
    gy, gx = np.gradient(h * h.shape[0] * 0.06)
    nrm = np.dstack([-gx, -gy, np.ones_like(h)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    L = np.array(light, float); L /= np.linalg.norm(L)
    lit = np.clip((nrm * L).sum(2), 0, 1)
    spec = np.clip((nrm * (L + [0, 0, 1]) / np.linalg.norm(L + [0, 0, 1])).sum(2), 0, 1) ** 24
    t = np.clip(0.18 + 0.82 * lit, 0, 1)
    # a chiselled look: faint broad facets, as the Face picture's stone has
    rng = np.random.default_rng(7)
    pts = rng.random((26, 2)) * h.shape[0]
    yy, xx = np.mgrid[0:h.shape[0], 0:h.shape[1]]
    cell = np.argmin(((yy[..., None] - pts[:, 1]) ** 2 + (xx[..., None] - pts[:, 0]) ** 2), axis=2)
    t = np.clip(t + (rng.random(26)[cell] - 0.5) * 0.06, 0, 1)
    rgb = np.dstack([np.interp(t, ramp[0], [c[i] for c in ramp[1]]) for i in range(3)])
    rgb = np.clip(rgb + spec[..., None] * 60, 0, 255)
    # its rim darker, as the pictures' figures are edged
    rim = _smooth((edge - 0.02) / 0.5) ** 0.6
    rgb *= (0.45 + 0.55 * rim)[..., None]
    return rgb


GOLD = ([0.0, 0.35, 0.7, 0.92, 1.0], [(70, 45, 0), (170, 120, 0), (226, 186, 14), (255, 236, 90), (255, 250, 170)])
GREY = ([0.0, 0.35, 0.7, 0.92, 1.0], [(40, 40, 42), (98, 97, 96), (150, 148, 146), (205, 204, 202), (245, 245, 245)])


def disc_only(piece):
    """The Face picture's ring and disc, its head painted out: the inner disc made again from the disc's own colour at
    each radius (read where the head isn't, between its edge and the ring), eased into the picture at the disc's edge."""
    a = piece.astype(np.float64)
    ph, pw = piece.shape[:2]; n = 256.0 * max(ph, pw) / 158.0 if max(ph, pw) < 200 else float(max(ph, pw))
    yy, xx = np.mgrid[0:ph, 0:pw]; rr = np.hypot(yy - (ph - 1) / 2, xx - (pw - 1) / 2)
    inner, outer = 0.118 * n, 0.148 * n              # the head lies within the first; the ring begins past the second
    prof = []
    for r0 in range(int(outer) + 2):
        band = (np.abs(rr - r0) < 1.0)
        rr0 = max(r0, inner)
        band = band if r0 >= inner else (np.abs(rr - inner) < 1.0)
        vals = a[band][:, :3]
        lum = vals.mean(1)
        keep = vals[lum <= np.percentile(lum, 60)]   # the disc, not a bright bit of the figure
        prof.append(keep.mean(0) if len(keep) else vals.mean(0))
    prof = np.array(prof)
    model = prof[np.clip(rr.round().astype(int), 0, len(prof) - 1)]
    w = _smooth((outer - rr) / (0.02 * n))[..., None]
    out = a.copy()
    out[..., :3] = model * w + a[..., :3] * (1 - w)
    return out.clip(0, 255).astype(np.uint8)


def figure_piece(head_piece, selected, size_frac=0.255):
    ph, pw = head_piece.shape[:2]
    # (the piece as the sheet has it, about 156 x 158, or padded to 256 square: its disc is the same size in both)
    n = 256.0 * max(ph, pw) / 158.0 if max(ph, pw) < 200 else float(max(ph, pw))
    base = disc_only(head_piece)
    m = int(round(n * size_frac))
    h, edge = torso_height(m * 2)                       # drawn at twice the size, then made smaller (smooth edges)
    rgb = shade(h, edge, GOLD if selected else GREY)
    fig = np.dstack([rgb, edge * 255]).clip(0, 255).astype(np.uint8)
    fig = np.array(Image.fromarray(fig).resize((m, int(m * 1.18)), Image.Resampling.LANCZOS))
    out = Image.fromarray(base)
    x0, y0 = (pw - fig.shape[1]) // 2, (ph - fig.shape[0]) // 2 + int(n * 0.005)
    if selected:                                        # the chosen picture's glow round its figure
        glow = np.zeros((ph, pw, 4), np.uint8)
        a = np.zeros((ph, pw), np.uint8); a[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig[..., 3]
        a = np.array(Image.fromarray(a).filter(ImageFilter.GaussianBlur(n / 40)))
        glow[..., 0], glow[..., 1], glow[..., 2], glow[..., 3] = 255, 210, 40, (a * 0.8).astype(np.uint8)
        out = Image.alpha_composite(out, Image.fromarray(glow))
    shadow = np.zeros((ph, pw, 4), np.uint8); a = np.zeros((ph, pw), np.uint8); a[y0 + 2:y0 + 2 + fig.shape[0], x0 + 2:x0 + 2 + fig.shape[1]] = fig[..., 3]
    shadow[..., 3] = (np.array(Image.fromarray(a).filter(ImageFilter.GaussianBlur(3))) * 0.6).astype(np.uint8)
    out = Image.alpha_composite(out, Image.fromarray(shadow))
    out.alpha_composite(Image.fromarray(fig), (x0, y0))
    return np.array(out)
