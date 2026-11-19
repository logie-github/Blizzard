#!/usr/bin/env python3
"""The Dark Troll's colours (docs/wrathpp/DARK_TROLLS.md): the Troll's own skins and hair colours, and more of the Night Elves' and of the
dark trolls' own (warcraft.wiki.gg/wiki/Dark_troll: grey to black skin; the RPG book's royal purple), each made by TINTING the Troll's texture
nearest in colour so that its mean colour is the wanted one (a per-channel factor, the picture's detail kept), body, underwear, faces and scalps
alike (one factor a new skin). The data names such a texture by a made-up file id (SYNTH and up) with a spec of how to make it; [Resolver]
makes it when the package step asks for the file (sl_looks.package wraps its reader with it), so no pixel is read when the data is made.

A spec: {"part": "body|pelvis|torso|face|hair|scalp", "group": a name (one new skin or colour: its parts choose the same Troll texture),
"like": a file id of today's (the colour wanted: its mean) or "like_rgb": [r, g, b], "cands": [{part: file id, ...}, ...] (the Troll's skins or
hair colours: body/pelvis/torso/face of each, or hair/scalp of each)}. The candidate whose "body" (or "hair") is nearest in colour to the
wanted one is the group's; the part is its [part], tinted by wanted mean / that candidate's mean."""
import math

import numpy as np

SYNTH = 2000000000
# The dark trolls' own skins (the wiki: gray to black; the RPG book: royal purple): name and the mean colour wanted.
OWN_SKINS = [("Ash Grey", (152, 152, 162)), ("Slate", (104, 106, 120)), ("Charcoal", (60, 60, 70)), ("Royal Purple", (112, 74, 150))]


def mean_rgb(rgba):
    """The mean colour of the picture's visible pixels."""
    visible = rgba[:, :, 3] > 8
    px = rgba[visible][:, :3] if visible.any() else rgba.reshape(-1, 4)[:, :3]
    return px.reshape(-1, 3).astype(np.float64).mean(axis=0)


def tinted(rgba, factor):
    out = rgba.copy()
    out[:, :, :3] = np.clip(rgba[:, :, :3].astype(np.float32) * np.asarray(factor, dtype=np.float32), 0, 255).astype(np.uint8)
    return out


def _hsv(rgb):
    """Hue (degrees), saturation and value of float RGB (0..255) arrays."""
    r, g, b = rgb[..., 0] / 255.0, rgb[..., 1] / 255.0, rgb[..., 2] / 255.0
    v = np.maximum(np.maximum(r, g), b)
    c = v - np.minimum(np.minimum(r, g), b)
    s = np.where(v > 0, c / np.maximum(v, 1e-6), 0.0)
    h = np.zeros_like(v)
    nz = c > 1e-6
    rc = nz & (v == r)
    gc = nz & (v == g) & ~rc
    bc = nz & ~rc & ~gc
    h[rc] = ((g - b)[rc] / c[rc]) % 6
    h[gc] = (b - r)[gc] / c[gc] + 2
    h[bc] = (r - g)[bc] / c[bc] + 4
    return h * 60.0, s, v


def skin_reference(rgba):
    """What a skin texture's skin is like: (hue in degrees, luminance of its skin pixels' mean), the pixels being the visible, saturated ones
    (a tusk, an eye's white and a loincloth are not the skin's colour)."""
    rgb = rgba[..., :3].astype(np.float64)
    h, s, v = _hsv(rgb)
    ok = (rgba[..., 3] > 8) & (s > 0.12) & (v > 0.06)
    if not ok.any():
        ok = rgba[..., 3] > 8
    ang = np.radians(h[ok])
    hue = float(np.degrees(np.arctan2((np.sin(ang) * s[ok]).sum(), (np.cos(ang) * s[ok]).sum())) % 360)
    lum = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
    return hue, float(max(lum[ok].mean(), 1.0))


def recolored(rgba, want, ref, width=80.0):
    """The picture with its skin's colour made [want] (r, g, b): each pixel whose hue is within [width] degrees of the reference skin's hue
    [ref] (from [skin_reference] of the Troll skin the colour was taken from) takes the wanted colour at its own brightness relative to the
    skin's mean (the shading, the veins and the folds kept, the same whatever the part: body, face, underwear), the nearer the hue the
    more fully; every other pixel (tusks, eye whites, loincloth, lips, tattoos of another colour) stays as it was. A per-channel factor (the
    first version) turned a blue skin's bright chest lilac and its dark legs and its face black."""
    hue0, lum0 = ref
    rgb = rgba[..., :3].astype(np.float64)
    h, s, v = _hsv(rgb)
    d = np.abs((h - hue0 + 180.0) % 360.0 - 180.0)
    w = np.clip(1.0 - d / width, 0.0, 1.0) * (s > 0.12) * (v > 0.04)
    lum = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
    shade = np.clip(lum / lum0, 0.0, 2.4)[..., None]
    target = np.clip(np.asarray(want, dtype=np.float64)[None, None, :] * shade, 0, 255)
    out = rgba.copy()
    out[..., :3] = np.clip(np.rint(rgb * (1 - w[..., None]) + target * w[..., None]), 0, 255).astype(np.uint8)
    return out


class Resolver:
    """A reader that makes a made-up file id's texture from its spec, and passes every other file id to [read]."""

    def __init__(self, read, specs):
        import blp
        self.blp, self.read, self.specs = blp, read, {str(k): v for k, v in specs.items()}
        self.cache, self.chosen, self.means, self.refs = {}, {}, {}, {}

    def texture(self, fid):
        if fid not in self.cache:
            self.cache[fid] = self.blp.read(self.read(fid))
        return self.cache[fid]

    def mean(self, fid):
        if fid not in self.means:
            self.means[fid] = mean_rgb(self.texture(fid))
        return self.means[fid]

    def wanted(self, spec):
        return np.asarray(spec["like_rgb"], dtype=np.float64) if "like_rgb" in spec else self.mean(spec["like"])

    def candidate(self, spec):
        """The group's Troll texture set nearest in colour (the same for each of the group's parts)."""
        group = spec["group"]
        if group not in self.chosen:
            want = np.maximum(self.wanted(spec), 1.0)
            key = "hair" if "hair" in spec["cands"][0] else "body"
            best = min(range(len(spec["cands"])),
                       key=lambda i: float(np.abs(np.log(np.maximum(self.mean(spec["cands"][i][key]), 1.0) / want)).sum()))
            self.chosen[group] = best
        return spec["cands"][self.chosen[group]]

    def __call__(self, fid):
        spec = self.specs.get(str(fid)) if isinstance(fid, int) and fid >= SYNTH else None
        if spec is None:
            return self.read(fid)
        cand = self.candidate(spec)
        key = "hair" if "hair" in cand else "body"
        if cand[key] not in self.refs:
            self.refs[cand[key]] = skin_reference(self.texture(cand[key]))
        return self.blp.write_dxt(recolored(self.texture(cand[spec["part"]]), self.wanted(spec), self.refs[cand[key]]), alpha=True)


def extend(dark, night_elf, own_skins=OWN_SKINS, first_id=SYNTH):
    """[dark] (the Troll's model data under the Dark Troll's folder: one sex) with the Night Elf [night_elf]'s skin and hair colours and the
    dark trolls' own skins added: new base skins (after the Troll's, in every tattoo block), a face texture a face on each, new hair colours
    (with their scalps); returns the specs of the made-up files and the new choices the creator lists ({option name: [choice rows]})."""
    specs, extra = {}, {"Skin Color": [], "Hair Color": []}
    counter = [first_id]

    def new(spec):
        counter[0] += 1
        specs[str(counter[0])] = spec
        return counter[0]

    troll_bases = dark["skins"][:dark["base_skins"]]
    n_old = len(troll_bases)
    faces = dark["faces"]
    colours = [("ne", s["choice"], {"like": s["body"]}, s) for s in night_elf["skins"][:night_elf["base_skins"]]]
    colours += [("own", "dt:" + name.lower().replace(" ", "-"), {"like_rgb": list(rgb)}, None) for name, rgb in own_skins]
    new_bases = []
    for j, (kind, choice, want, ne_skin) in enumerate(colours):
        group = "skin:%d:%s" % (j, dark["name"])
        cands = []
        for b in troll_bases:
            cand = {"body": b["body"], "pelvis": b["pelvis"], "torso": b["torso"]}
            for fi, f in enumerate(faces):
                cand["face%d" % fi] = f["textures"].get(str(b["base"])) or 0
            cands.append(cand)

        def part(name, present=True, key=None):
            return new(dict(want, part=key or name, group=group, cands=cands)) if present else 0
        base = {"choice": choice, "order": 1000 + j, "body": part("body"),
                "pelvis": part("pelvis", any(c["pelvis"] for c in cands)), "torso": part("torso", any(c["torso"] for c in cands))}
        new_bases.append(base)
        for fi, f in enumerate(faces):
            f["textures"][str(n_old + j)] = part("face%d" % fi, any(c["face%d" % fi] for c in cands))
        n_ne = len(night_elf["skins"][:night_elf["base_skins"]])
        row = {"ID": choice, "Name_lang": ("" if kind == "ne" else own_skins[j - n_ne][0]),
               "ChrCustomizationReqID": "0", "SwatchColor_0": "0", "SwatchColor_1": "0"}
        extra["Skin Color"].append(row)
    for f in faces:
        f["skins"] = sorted(set(f["skins"]) | set(range(n_old, n_old + len(new_bases))))
    # the skins: for each tattoo block of the Troll's, its base skins and then the new ones
    blocks = {}
    for s in dark["skins"]:
        blocks.setdefault((s["tattoo_name"]), []).append(s)
    skins = []
    for tname, block in blocks.items():
        for s in block:
            skins.append(dict(s, index=len(skins)))
        for j, b in enumerate(new_bases):
            skins.append(dict(b, index=len(skins), base=n_old + j, tattoo=block[0]["tattoo"], tattoo_name=tname))
    dark["skins"] = skins
    dark["base_skins"] = n_old + len(new_bases)
    # hair colours: the Night Elf's, each the Troll's hair nearest in colour tinted; a scalp per colour where the Troll's hair styles have one
    troll_hair = dark["hair_colors"]
    cands = []
    for hc in troll_hair:
        cand = {"hair": hc["file"]}
        for hi, h in enumerate(dark.get("hair", [])):
            sc = h.get("scalp", {})
            cand["scalp%d" % hi] = sc.get(str(hc["index"])) or sc.get("*") or 0
        cands.append(cand)
    for k, hc in enumerate(night_elf["hair_colors"]):
        group = "hair:%d:%s" % (k, dark["name"])
        want = {"like": hc["file"]}
        entry = {"index": len(dark["hair_colors"]), "file": new(dict(want, part="hair", group=group, cands=cands)), "choice": hc["choice"]}
        for hi, h in enumerate(dark.get("hair", [])):
            sc = h.get("scalp", {})
            if sc and "*" not in sc and any(c["scalp%d" % hi] for c in cands):
                sc[str(entry["index"])] = new(dict(want, part="scalp%d" % hi, group=group, cands=cands))
        dark["hair_colors"].append(entry)
        extra["Hair Color"].append({"ID": hc["choice"], "Name_lang": "", "ChrCustomizationReqID": "0", "SwatchColor_0": "0", "SwatchColor_1": "0"})
    return specs, extra
