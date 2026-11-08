"""What the starting areas' tools share: the Cataclysm game they come from (Cataclysm Classic, at one
build, on wago.tools), its tables, 3.3.5a's tables' layouts (WoWDBDefs) and the maps.

Every fetch is cached in a folder of the caller's (CACHE): a file by its id, a table by its name, both
at BUILD, so a run again fetches nothing.
"""
import csv
import io
import os
import re
import struct
import time
import urllib.error
import urllib.request

# Cataclysm Classic's last build: its world, models and tables are Cataclysm's (4.3.4's ids), in
# today's formats (the converter's input).
BUILD = "4.4.2.60895"
# Wrath Classic's last build: its files are 3.3.5a's (the few it added aside), for telling the game's
# own buildings from Cataclysm's where only a 3.3.5a client could say (wrath_has).
WRATH_BUILD = "3.4.5.63697"
USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"   # (wago.tools turns away Python's own)

# The starting areas' maps: Gilneas (the Worgen's) and the Lost Isles (Kezan and the Lost Isles: the
# Goblins'), and the maps their terrain is swapped with as the story goes (made into whole maps of
# their own here: 3.3.5a can't swap a map's terrain).
MAPS = {
    654: "Gilneas2",           # Gilneas: the Worgen's start
    638: "Gilneas",            # Gilneas's terrain until quest 14222 is turned in (the city whole)
    655: "GilneasPhase1",      # from quest 14386 on (Duskmist Shore broken)
    656: "GilneasPhase2",
    648: "LostIsles",          # Kezan and the Lost Isles: the Goblins' start
    659: "LostIslesPhase1",    # the volcano's eruption
    661: "LostIslesPhase2",    # Town in a Box
}
# Each terrain swap's base map: its tiles are the base's with its own in their places.
OVERLAYS = {638: 654, 655: 654, 656: 654, 659: 648, 661: 648}


def fetch_url(url, tries=6):
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                raise
            err = e
        except Exception as e:     # (a dropped connection, a timeout: tried again)
            err = e
        time.sleep(min(60, 2 ** attempt))
    raise IOError(f"{url}: {err}")


def file_bytes(cache, fdid):
    """A file of the game by its id, at BUILD (b"" when the build hasn't it)."""
    path = os.path.join(cache, "files", str(fdid))
    if os.path.exists(path):
        return open(path, "rb").read()
    try:
        data = fetch_url(f"https://wago.tools/api/casc/{fdid}?download&version={BUILD}")
    except urllib.error.HTTPError:
        data = b""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".part", "wb") as f:
        f.write(data)
    os.replace(path + ".part", path)
    return data


def wrath_has(cache, fdid):
    """Whether Wrath's game has a file (by its id): Wrath Classic's build has it."""
    path = os.path.join(cache, "wrath", str(fdid))
    if not os.path.exists(path):
        try:
            data = fetch_url(f"https://wago.tools/api/casc/{fdid}?download&version={WRATH_BUILD}")
        except urllib.error.HTTPError:
            data = b""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("1" if data else "0")
    return open(path).read() == "1"


def table(cache, name):
    """A table of the game at BUILD, as rows of text by column name."""
    path = os.path.join(cache, "tables", name + ".csv")
    if not os.path.exists(path):
        data = fetch_url(f"https://wago.tools/db2/{name}/csv?build={BUILD}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".part", "wb") as f:
            f.write(data)
        os.replace(path + ".part", path)
    return list(csv.DictReader(io.StringIO(open(path, encoding="utf-8").read())))


# The graveyards' places: not in the game's tables since Cataclysm Classic (the server's own), so
# TrinityCore's, as it moved them out of WorldSafeLocs.dbc into its world (the same ids).
SAFE_LOCS = ("https://raw.githubusercontent.com/TrinityCore/TrinityCore/e0eec525aa505be993400a9b84ab074ace8e50a1/"
             "sql/old/8.x/world/19071_2020_06_17/2019_10_26_01_world.sql")


def world_safe_locs(cache):
    """{id: (map, x, y, z, facing in degrees, name)}."""
    path = os.path.join(cache, "world_safe_locs.sql")
    if not os.path.exists(path):
        data = fetch_url(SAFE_LOCS)
        with open(path + ".part", "wb") as f:
            f.write(data)
        os.replace(path + ".part", path)
    out = {}
    for m in re.finditer(r"^\((\d+),(\d+),([-\d.e]+),([-\d.e]+),([-\d.e]+),([-\d.e]+),'((?:[^'\\]|\\.)*)'\)",
                         open(path, encoding="utf-8").read(), re.M):
        out[int(m[1])] = (int(m[2]), float(m[3]), float(m[4]), float(m[5]), float(m[6]), m[7].replace("\\'", "'"))
    return out


def listfile(path):
    """The community listfile (id;path) as {id: path} and {path: id}, paths in lower case."""
    by_id, by_path = {}, {}
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\r\n")
        if ";" not in line:
            continue
        i, p = line.split(";", 1)
        by_id[int(i)] = p.lower()
        by_path[p.lower()] = int(i)
    return by_id, by_path


# The tables whose 3.3.5a definition in WoWDBDefs leaves fields unnamed (and so typed float, a seat's
# flags among them): their fields as AzerothCore's own (DBCfmt.h, its *_dbc tables), named as
# Cataclysm Classic's columns are; a float's name starts with a dot.
LAYOUTS = {
    "VehicleSeat": [(c.lstrip("."), "f" if c[0] == "." else "i") for c in (
        "ID", "Flags", "AttachmentID", ".AttachmentOffset_0", ".AttachmentOffset_1", ".AttachmentOffset_2",
        ".EnterPreDelay", ".EnterSpeed", ".EnterGravity", ".EnterMinDuration", ".EnterMaxDuration",
        ".EnterMinArcHeight", ".EnterMaxArcHeight", "EnterAnimStart", "EnterAnimLoop", "RideAnimStart",
        "RideAnimLoop", "RideUpperAnimStart", "RideUpperAnimLoop", ".ExitPreDelay", ".ExitSpeed", ".ExitGravity",
        ".ExitMinDuration", ".ExitMaxDuration", ".ExitMinArcHeight", ".ExitMaxArcHeight", "ExitAnimStart",
        "ExitAnimLoop", "ExitAnimEnd", ".PassengerYaw", ".PassengerPitch", ".PassengerRoll", "PassengerAttachmentID",
        "VehicleEnterAnim", "VehicleExitAnim", "VehicleRideAnimLoop", "VehicleEnterAnimBone", "VehicleExitAnimBone",
        "VehicleRideAnimLoopBone", ".VehicleEnterAnimDelay", ".VehicleExitAnimDelay", "VehicleAbilityDisplay",
        "EnterUISoundID", "ExitUISoundID", "UiSkin", "FlagsB", ".CameraEnteringDelay", ".CameraEnteringDuration",
        ".CameraExitingDelay", ".CameraExitingDuration", ".CameraOffset_0", ".CameraOffset_1", ".CameraOffset_2",
        ".CameraPosChaseRate", ".CameraFacingChaseRate", ".CameraEnteringZoom", ".CameraSeatZoomMin",
        ".CameraSeatZoomMax")],
}


def layout(dbd_dir, name, build="3.3.5.12340"):
    """A table's fields in 3.3.5a, from its WoWDBDefs definition: [(column, type)], type "i" (32-bit
    integer), "f" (float) or "s" (text); a localized text is its 16 languages' texts and their flags
    (17 fields, the first named after the column), an array one field a value (column_0, column_1...)."""
    if name in LAYOUTS and build == "3.3.5.12340":
        return list(LAYOUTS[name])
    text = open(os.path.join(dbd_dir, name + ".dbd"), encoding="utf-8").read()
    kinds = {}
    for m in re.finditer(r"^(int|uint|float|string|locstring)(?:<[^>]*>)?\s+(\w+)", text.split("\n\n")[0], re.M):
        kinds[m.group(2)] = m.group(1)
    for block in text.split("\n\n")[1:]:
        lines = block.strip().split("\n")
        builds = [l for l in lines if l.startswith("BUILD ")]
        if not any(_has_build(l[6:], build) for l in builds):
            continue
        fields = []
        for l in lines:
            if l.startswith(("BUILD", "LAYOUT", "COMMENT")) or not l.strip():
                continue
            m = re.match(r"(?:\$[^$]*\$)?(\w+)(?:<(u?)(\d+)>)?(?:\[(\d+)\])?", l.strip())
            col, count = m.group(1), int(m.group(4) or 1)
            kind = kinds[col]
            for n in range(count):
                cname = col if count == 1 else f"{col}_{n}"
                if kind == "locstring":
                    fields.append((cname, "s"))
                    fields += [(f"{cname}#{k}", "s") for k in range(1, 16)]
                    fields.append((f"{cname}#flags", "i"))
                elif kind == "string":
                    fields.append((cname, "s"))
                elif kind == "float":
                    fields.append((cname, "f"))
                else:
                    fields.append((cname, "i"))
        return fields
    raise KeyError(f"{name}: no layout for {build}")


def _has_build(spec, build):
    def key(b):
        return tuple(int(x) for x in b.split("."))
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-")
            if key(lo) <= key(build) <= key(hi):
                return True
        elif part == build:
            return True
    return False


class Dbc:
    """A 3.3.5a table (the game's own, the server's data folder's): rows by id, as values."""

    def __init__(self, path, fields=None):
        data = open(path, "rb").read()
        magic, count, nfields, size, _ = struct.unpack("<4s4I", data[:20])
        assert magic == b"WDBC", path
        self.count, self.nfields = count, nfields
        self.raw = [data[20 + i * size:20 + (i + 1) * size] for i in range(count)]
        self.text = data[20 + count * size:]
        self.fields = fields

    def s(self, offset):
        return self.text[offset:self.text.index(b"\0", offset)].decode("utf-8", "replace")

    def rows(self):
        types = [t for _, t in self.fields] if self.fields else "i" * self.nfields
        for raw in self.raw:
            ints = struct.unpack(f"<{len(types)}I", raw[:4 * len(types)])
            row = []
            for v, t in zip(ints, types):
                row.append(self.s(v) if t == "s" else struct.unpack("<f", struct.pack("<I", v))[0] if t == "f" else v)
            yield row

    def ids(self):
        return {struct.unpack_from("<I", r)[0] for r in self.raw}


def stock_ids(stock_dir, name):
    """A 3.3.5a table's ids alone (its records' first field), for one whose layout has fields
    narrower than four bytes (PowerDisplay's colours), which Dbc doesn't read."""
    for f in os.listdir(stock_dir):
        if f.lower() == name.lower() + ".dbc":
            raw = open(os.path.join(stock_dir, f), "rb").read()
            _, records, _, size, _ = struct.unpack("<4s4I", raw[:20])
            return {struct.unpack_from("<I", raw, 20 + i * size)[0] for i in range(records)}
    raise FileNotFoundError(name)


def stock(stock_dir, name, dbd_dir=None):
    for f in os.listdir(stock_dir):
        if f.lower() == name.lower() + ".dbc":
            return Dbc(os.path.join(stock_dir, f), layout(dbd_dir, name) if dbd_dir else None)
    raise FileNotFoundError(name)
