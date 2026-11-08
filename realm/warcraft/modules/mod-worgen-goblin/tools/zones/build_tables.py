#!/usr/bin/env python3
"""The starting areas' rows in the game's tables and the world server's: their maps, areas, lights,
music and ambience, loading screens and world maps, from Cataclysm Classic's tables (common.BUILD),
written in 3.3.5a's layouts.

Nothing of 3.3.5a's is changed: every row here is a new one. A row keeps Cataclysm's id where 3.3.5a
and the realm's other modules have no row of that id; where they have one (a different thing of the
same number) it gets a new id, and what names it is renumbered with it. A row 3.3.5a already has as it
is (the same sound, the same files) is used as it is.

Used by build_world.py (the starting areas' whole build), which writes, besides its own:
  - data/zones/client/dbc/<Table>.txt: the rows for the game's patch (mod-skyborne's format);
  - data/zones/server/zones_dbc.sql: the same for the world server's *_dbc tables;
  - data/zones/files.tsv: the game's files they name, with the maps' own and everything those use.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import common  # noqa: E402
from build_data import columns, esc  # noqa: E402

OUT = os.path.join(MODULE, "data", "zones")
# The tables the world server reads (its *_dbc table over each).
SERVER = {
    "Map": "map_dbc", "AreaTable": "areatable_dbc", "Light": "light_dbc", "WMOAreaTable": "wmoareatable_dbc",
    "WorldMapArea": "worldmaparea_dbc", "WorldMapOverlay": "worldmapoverlay_dbc", "SoundEntries": "soundentries_dbc",
    "CreatureDisplayInfo": "creaturedisplayinfo_dbc", "CreatureDisplayInfoExtra": "creaturedisplayinfoextra_dbc",
    "CreatureModelData": "creaturemodeldata_dbc", "Faction": "faction_dbc", "FactionTemplate": "factiontemplate_dbc",
    "GameObjectDisplayInfo": "gameobjectdisplayinfo_dbc", "Spell": "spell_dbc", "Item": "item_dbc",
    "ItemDisplayInfo": "itemdisplayinfo_dbc", "SpellCastTimes": "spellcasttimes_dbc", "SpellDuration": "spellduration_dbc",
    "SpellRange": "spellrange_dbc", "SpellRadius": "spellradius_dbc", "SummonProperties": "summonproperties_dbc",
    "Vehicle": "vehicle_dbc", "VehicleSeat": "vehicleseat_dbc", "CinematicSequences": "cinematicsequences_dbc",
    "CinematicCamera": "cinematiccamera_dbc",
}
# New ids, where Cataclysm's are taken: from just past the highest of 3.3.5a's own (the game sizes some
# tables' lookups by their highest id), or from here for these.
NEW_IDS = {"LightParams": 9000, "LoadingScreens": 8800, "WorldMapArea": 8800}
# 3.3.5a's own exploration bits end at 3617 and a character has 4096 (128 fields of 32): Cataclysm's
# past that are given free ones, from here.
FREE_AREA_BITS = range(3618, 4096)
# Cataclysm's area flags that mean something else in 3.3.5a (or nothing): expansion-only flying
# (0x400, 0x4000), Wintergrasp (0x01000000), "no local defense channel", 3.3.5a's no-flying (0x20000000:
# Cataclysm's ghost bind), "is a subzone" and its last; and the bits 3.3.5a doesn't use.
AREA_FLAGS_DROPPED = 0x400 | 0x2000 | 0x4000 | 0x20000 | 0x01000000 | 0x10000000 | 0x20000000 | 0x40000000 | 0x80000000
# 3.3.5a's LightParams, as its own rows have them (WoWDBDefs names a field it hasn't, and not the cloud
# type it has): checked on the rows Cataclysm kept the same.
LIGHT_PARAMS = [("ID", "i"), ("HighlightSky", "i"), ("LightSkyboxID", "i"), ("CloudTypeID", "i"), ("Glow", "f"),
                ("WaterShallowAlpha", "f"), ("WaterDeepAlpha", "f"), ("OceanShallowAlpha", "f"), ("OceanDeepAlpha", "f")]
# LightIntBand's 18 colours of a LightParams, in order, as Cataclysm's LightData names them (checked
# against 3.3.5a's own bands of the lights both have), and LightFloatBand's six numbers.
INT_BANDS = ["DirectColor", "AmbientColor", "SkyTopColor", "SkyMiddleColor", "SkyBand1Color", "SkyBand2Color",
             "SkySmogColor", "SkyFogColor", "ShadowOpacity", "SunColor", "CloudSunColor", "CloudLayer1AmbientColor",
             "CloudEmissiveColor", "CloudLayer2AmbientColor", "OceanCloseColor", "OceanFarColor", "RiverCloseColor",
             "RiverFarColor"]
FLOAT_BANDS = ["FogEnd", "FogScaler", None, "CloudDensity", None, None]
FLOAT_BAND_DEFAULTS = [0.0, 0.0, 1.0, 0.0, 0.95, 1.0]     # (3.3.5a's own for the ones Cataclysm hasn't)
# The world maps: Cataclysm's UiMap of each zone, and which art each of the realm's maps shows.
WORLD_MAPS = {
    # UiMap: (zone, maps it's on, its art on each, parent UiMap)
    179: (4714, {654: 184, 638: 184, 655: 216, 656: 220}, None),     # Gilneas
    202: (4755, {654: 207, 638: 207}, 179),                          # Gilneas City
    174: (4720, {648: 179, 659: 225, 661: 226}, None),               # The Lost Isles
    194: (4737, {648: 199, 659: 199, 661: 199}, None),               # Kezan
}


# The two races' new characters' starts (all but the death knights, who start at Ebon Hold): with the
# starting areas, Cataclysm's (the Cataclysm Preservation Project's playercreateinfo; the Worgen's on
# Gilneas as it is until quest 14222, map 638 here); without them, mod-worgoblin's (its worgoblin.sql).
STARTS_ON = {12: (638, 4756, -1451.53, 1403.35, 35.5561, 0.333847), 9: (648, 4765, -8423.81, 1361.3, 104.671, 1.55428)}
STARTS_OFF = {12: (1, 141, 10311.3, 832.463, 1326.41, 5.69632), 9: (1, 14, -618.518, -4251.67, 38.718, 0.0)}
# Their intro (the camera flight a new character's first login shows): with the starting areas,
# Cataclysm's own (ChrRaces' CinematicSequenceID: the flight over Gilneas with the Worgen's narration,
# over Kezan with the Goblins'), as the rows the build makes of them; without, mod-worgoblin's (the
# Night Elves' and the Orcs' flights, CinematicSequences 61 and 141 in its chrraces_dbc rows).
INTROS_CATACLYSM = {12: 170, 9: 172}
INTROS_OFF = {12: 61, 9: 141}
CHRRACES_CINEMATIC = 12                        # (ChrRaces' CinematicSequenceID field in 3.3.5a)


def intros_sql(intros):
    return "".join(f"UPDATE `chrraces_dbc` SET `CinematicSequenceID` = {seq} WHERE `ID` = {race};\n"
                   for race, seq in sorted(intros.items()) if seq)


def starts_sql(starts):
    return "".join(f"UPDATE `playercreateinfo` SET `map` = {m}, `zone` = {z}, `position_x` = {x}, `position_y` = {y}, "
                   f"`position_z` = {h}, `orientation` = {o} WHERE `race` = {race} AND `class` <> 6;\n"
                   for race, (m, z, x, y, h, o) in sorted(starts.items()))


def light_coords(x, y, z):
    """Cataclysm's light position (the world's own) as 3.3.5a stores it."""
    return (17066.666 - y) * 36, z * 36, (17066.666 - x) * 36


class Ids:
    """Each table's ids: 3.3.5a's own, the other modules', and the ones given out here."""

    def __init__(self, stock_dir, dbd):
        self.stock_dir, self.dbd = stock_dir, dbd
        self.taken, self.given, self.rows_cache = {}, {}, {}
        self.others = others_ids()

    def stock_rows(self, table):
        if table not in self.rows_cache:
            self.rows_cache[table] = {r[0]: r for r in common.stock(self.stock_dir, table, None if table == "LightParams" else self.dbd).rows()}
        return self.rows_cache[table]

    def stock_ids(self, table):
        try:
            return common.stock(self.stock_dir, table).ids()
        except FileNotFoundError:
            return set()

    def taken_ids(self, table):
        if table not in self.taken:
            try:
                ids = common.stock(self.stock_dir, table).ids()
            except FileNotFoundError:
                ids = set()
            self.taken[table] = ids | self.others.get(table, set())
        return self.taken[table]

    def new(self, table, want=None):
        taken = self.taken_ids(table)
        if want is not None and want > 0 and want not in taken:
            taken.add(want)
            return want
        if table not in self.given:
            stock = self.stock_ids(table)
            self.given[table] = NEW_IDS.get(table) or (max(stock) + 1 if stock else 1)
        start = self.given[table]
        while start in taken:
            start += 1
        taken.add(start)
        self.given[table] = start + 1
        return start


def others_ids():
    """The ids the realm's other modules put in each table (their data/client/dbc/*.txt)."""
    found = {}
    root = os.path.dirname(MODULE)
    for module in sorted(os.listdir(root)):
        folder = os.path.join(root, module, "data", "client", "dbc")
        if not os.path.isdir(folder):
            continue
        for name in os.listdir(folder):
            if not name.endswith(".txt"):
                continue
            ids = found.setdefault(name[:-4], set())
            for line in open(os.path.join(folder, name), encoding="utf-8"):
                parts = line.split("\t")
                if parts[0] in ("put", "copyrow") and len(parts) > 2:
                    ids.add(int(parts[2] if parts[0] == "copyrow" else parts[1]))
    return found


class Tables:
    def __init__(self, dbd):
        self.dbd = dbd
        self.rows = {}
        self.sets = {}                # table: [(id, field, value)], a change to a row the game has
        self.intros = {}              # race: its intro's CinematicSequences row (INTROS_CATACLYSM)

    def fields(self, table):
        return LIGHT_PARAMS if table == "LightParams" else common.layout(self.dbd, table)

    def add(self, table, values):
        """A row by its columns' names (a localized text's English only; the rest 0 or empty)."""
        row = []
        for name, kind in self.fields(table):
            v = values.get(name)
            if v is None:
                v = "" if kind == "s" else 0
            row.append(v)
        unknown = set(values) - {n for n, _ in self.fields(table)}
        assert not unknown, (table, unknown)
        self.rows.setdefault(table, []).append(row)
        return row

    def set(self, table, row_id, field, value):
        """A field of a row the game (or mod-worgoblin's tables) has, changed in the game's patch."""
        self.sets.setdefault(table, []).append((row_id, field, value))

    def write(self, core):
        folder = os.path.join(OUT, "client", "dbc")
        os.makedirs(folder, exist_ok=True)
        for old in os.listdir(folder):
            os.remove(os.path.join(folder, old))
        sql = ["-- The starting areas' rows in the world server's tables (tools/zones/build_tables.py): run by",
               "-- src/WorgenGoblin.cpp at every start of ChromieCraft's world server, with the starting areas",
               "-- installed. New rows only (3.3.5a's own are never changed)."]
        for table, sets in sorted(self.sets.items()):
            if table not in self.rows:
                with open(os.path.join(folder, table + ".txt"), "w", newline="\n") as f:
                    f.write(f"# {table}: the starting areas' changes to rows the game has (tools/zones/build_tables.py)\n")
                    f.writelines(f"set\t{i}\t{field}\t{value}\n" for i, field, value in sorted(sets))
        for table, rows in sorted(self.rows.items()):
            fields = self.fields(table)
            types = "".join(k for _, k in fields)
            rows.sort(key=lambda r: r[0])
            with open(os.path.join(folder, table + ".txt"), "w", newline="\n") as f:
                f.write(f"# {table}: the starting areas (tools/zones/build_tables.py)\ntypes\t{types}\n")
                for r in rows:
                    f.write("put\t" + "\t".join(cell(v, k) for v, k in zip(r, types)) + "\n")
                f.writelines(f"set\t{i}\t{field}\t{value}\n" for i, field, value in sorted(self.sets.get(table, [])))
            if table in SERVER:
                cols = columns(core, SERVER[table])
                assert len(cols) == len(fields), (table, len(cols), len(fields))
                names = ", ".join(f"`{c}`" for c, _ in cols)
                update = ", ".join(f"`{c}` = VALUES(`{c}`)" for c, _ in cols[1:])
                for i in range(0, len(rows), 200):
                    values = ",\n".join("(" + ", ".join(sql_cell(v, k, u) for v, k, (_, u) in zip(r, types, cols)) + ")"
                                        for r in rows[i:i + 200])
                    sql.append(f"INSERT INTO `{SERVER[table]}` ({names}) VALUES\n{values}\nON DUPLICATE KEY UPDATE {update};")
        os.makedirs(os.path.join(OUT, "server"), exist_ok=True)
        with open(os.path.join(OUT, "server", "zones_dbc.sql"), "w", newline="\n") as f:
            f.write("\n".join(sql) + "\n")
        # Without the starting areas: their rows out of the world server's tables, the starts back.
        off = ["-- No starting areas (tools/zones/build_tables.py): their rows out of the world server's tables,",
               "-- the Worgen's and Goblins' starts back where mod-worgoblin has them."]
        for table, rows in sorted(self.rows.items()):
            if table in SERVER:
                key = columns(core, SERVER[table])[0][0]
                ids = sorted(r[0] for r in rows)
                for i in range(0, len(ids), 500):
                    off.append(f"DELETE FROM `{SERVER[table]}` WHERE `{key}` IN ({', '.join(str(x) for x in ids[i:i + 500])});")
        with open(os.path.join(OUT, "server", "zones_off.sql"), "w", newline="\n") as f:
            f.write("\n".join(off) + "\n" + starts_sql(STARTS_OFF) + intros_sql(INTROS_OFF))
        with open(os.path.join(OUT, "server", "starts_on.sql"), "w", newline="\n") as f:
            f.write("-- The Worgen's and Goblins' new characters start in their starting areas (tools/zones/build_tables.py).\n"
                    + starts_sql(STARTS_ON) + intros_sql(self.intros))


def cell(v, kind):
    if kind == "s":
        return esc(v)
    if kind == "f":
        return repr(float(v))
    return str(int(v) & 0xFFFFFFFF)


def sql_cell(v, kind, unsigned):
    if kind == "s":
        return "'" + str(v).replace("\\", "\\\\").replace("'", "\\'") + "'"
    if kind == "f":
        return repr(float(v))
    v = int(v) & 0xFFFFFFFF
    return str(v if unsigned or v < 0x80000000 else v - 0x100000000)


def num(text):
    return float(text) if "." in text or "e" in text.lower() else int(text)


def game_path(path):
    return path.replace("/", "\\")


class Builder:
    def __init__(self, cache, stock_dir, dbd, listfile):
        self.cache = cache
        self.ids = Ids(stock_dir, dbd)
        self.out = Tables(dbd)
        self.names, self.fdids = common.listfile(listfile)
        self.files = {}               # fdid: (path, kind)
        self.done = {}                # (table, cataclysm id): our id
        self.t = {}

    def table(self, name):
        if name not in self.t:
            self.t[name] = common.table(self.cache, name)
        return self.t[name]

    def by_id(self, name):
        key = ("by_id", name)
        if key not in self.t:
            self.t[key] = {int(r["ID"]): r for r in self.table(name)}
        return self.t[key]

    def kit_entries(self, kit_id):
        if "kit_entries" not in self.t:
            index = {}
            for e in self.table("SoundKitEntry"):
                index.setdefault(int(e["SoundKitID"]), []).append(e)
            self.t["kit_entries"] = index
        return self.t["kit_entries"].get(int(kit_id), [])

    def file(self, fdid, kind):
        """A file of the game by its id (in the patch with its listfile path), as the path 3.3.5a names it by."""
        path = self.names.get(int(fdid))
        if not path:
            raise KeyError(f"file {fdid} isn't in the listfile")
        self.files[int(fdid)] = (path, kind)
        return path

    # --- Sounds -------------------------------------------------------------------------------------

    def sound(self, kit_id):
        """A SoundKit as a SoundEntries row (3.3.5a's own when it has the same one); 0 for none."""
        kit_id = int(kit_id)
        if kit_id <= 0:
            return 0
        key = ("SoundEntries", kit_id)
        if key in self.done:
            return self.done[key]
        kit = self.by_id("SoundKit").get(kit_id)
        if kit is None:
            return 0
        entries = self.kit_entries(kit_id)[:10]
        paths, freqs = [], []
        for e in entries:
            try:
                paths.append(self.file(e["FileDataID"], "sound"))
            except KeyError:
                continue
            freqs.append(int(float(e["Frequency"])))
        if not paths:
            return 0
        base = os.path.commonpath([os.path.dirname(p) for p in paths])
        files = [os.path.relpath(p, base).replace("/", "\\") for p in paths]
        stock = self.ids.stock_rows("SoundEntries").get(kit_id)
        if stock is not None and [x.lower() for x in stock[3:3 + len(files)]] == [f.lower() for f in files] \
                and stock[23].lower() == game_path(base).lower():
            self.done[key] = kit_id
            return kit_id
        our = self.ids.new("SoundEntries", kit_id)
        values = {"ID": our, "SoundType": int(kit["SoundType"]), "Name": f"Cataclysm{kit_id}",
                  "DirectoryBase": game_path(base), "VolumeFloat": float(kit["VolumeFloat"]),
                  "Flags": int(kit["Flags"]) & 0xFFFF, "MinDistance": float(kit["MinDistance"]),
                  "DistanceCutoff": float(kit["DistanceCutoff"]), "EAXDef": int(kit["EAXDef"])}
        for n, (f, q) in enumerate(zip(files, freqs)):
            values[f"File_{n}"] = f
            values[f"Freq_{n}"] = q
        self.out.add("SoundEntries", values)
        self.done[key] = our
        return our

    def ambience(self, cata_id):
        cata_id = int(cata_id)
        if cata_id <= 0:
            return 0
        key = ("SoundAmbience", cata_id)
        if key not in self.done:
            r = self.by_id("SoundAmbience")[cata_id]
            day, night = self.sound(r["AmbienceID_0"]), self.sound(r["AmbienceID_1"])
            stock = self.ids.stock_rows("SoundAmbience").get(cata_id)
            if stock is not None and stock[1:3] == [day, night]:
                self.done[key] = cata_id
            else:
                our = self.ids.new("SoundAmbience", cata_id)
                self.out.add("SoundAmbience", {"ID": our, "AmbienceID_0": day, "AmbienceID_1": night})
                self.done[key] = our
        return self.done[key]

    def music(self, cata_id):
        cata_id = int(cata_id)
        if cata_id <= 0:
            return 0
        key = ("ZoneMusic", cata_id)
        if key not in self.done:
            r = self.by_id("ZoneMusic")[cata_id]
            values = {"SetName": r["SetName"], "Sounds_0": self.sound(r["Sounds_0"]), "Sounds_1": self.sound(r["Sounds_1"])}
            for c in ("SilenceIntervalMin_0", "SilenceIntervalMin_1", "SilenceIntervalMax_0", "SilenceIntervalMax_1"):
                values[c] = int(r[c])
            stock = self.ids.stock_rows("ZoneMusic").get(cata_id)
            if stock is not None and stock[6:8] == [values["Sounds_0"], values["Sounds_1"]]:
                self.done[key] = cata_id
            else:
                values["ID"] = self.ids.new("ZoneMusic", cata_id)
                self.out.add("ZoneMusic", values)
                self.done[key] = values["ID"]
        return self.done[key]

    def intro(self, cata_id):
        cata_id = int(cata_id)
        if cata_id <= 0:
            return 0
        key = ("ZoneIntroMusicTable", cata_id)
        if key not in self.done:
            r = self.by_id("ZoneIntroMusicTable")[cata_id]
            values = {"Name": r["Name"], "SoundID": self.sound(r["SoundID"]), "Priority": int(r["Priority"]),
                      "MinDelayMinutes": int(r["MinDelayMinutes"])}
            stock = self.ids.stock_rows("ZoneIntroMusicTable").get(cata_id)
            if stock is not None and stock[2] == values["SoundID"]:
                self.done[key] = cata_id
            else:
                values["ID"] = self.ids.new("ZoneIntroMusicTable", cata_id)
                self.out.add("ZoneIntroMusicTable", values)
                self.done[key] = values["ID"]
        return self.done[key]

    def provider(self, cata_id):
        cata_id = int(cata_id)
        if cata_id <= 0:
            return 0
        key = ("SoundProviderPreferences", cata_id)
        if key not in self.done:
            r = self.by_id("SoundProviderPreferences")[cata_id]
            values = {c: (float(r[c]) if k == "f" else int(float(r[c]))) for c, k in self.out.fields("SoundProviderPreferences")
                      if c in r and c not in ("ID", "Description")}
            values["Description"] = r["Description"]
            stock = self.ids.stock_rows("SoundProviderPreferences").get(cata_id)
            if stock is not None and stock[1] == r["Description"]:
                self.done[key] = cata_id
            else:
                values["ID"] = self.ids.new("SoundProviderPreferences", cata_id)
                self.out.add("SoundProviderPreferences", values)
                self.done[key] = values["ID"]
        return self.done[key]

    # --- Maps and areas -----------------------------------------------------------------------------

    def loading_screen(self, cata_id):
        cata_id = int(cata_id)
        if cata_id <= 0:
            return 0
        key = ("LoadingScreens", cata_id)
        if key not in self.done:
            r = self.by_id("LoadingScreens")[cata_id]
            narrow = self.file(r["NarrowScreenFileDataID"], "ui")
            wide = int(r["WideScreenFileDataID"])
            if wide:
                self.file(wide, "ui")
            our = self.ids.new("LoadingScreens")
            name = os.path.splitext(os.path.basename(narrow))[0]
            self.out.add("LoadingScreens", {"ID": our, "Name": f"Cataclysm{name}", "FileName": game_path(narrow),
                                             "HasWideScreen": 1 if wide else 0})
            self.done[key] = our
        return self.done[key]

    def maps(self):
        cata = self.by_id("Map")
        stock_flags = self.ids.stock_rows("Map")[0][3]          # (Eastern Kingdoms': a continent's)
        for map_id, directory in common.MAPS.items():
            r = cata[map_id]
            assert r["Directory"] == directory, (map_id, r["Directory"])
            assert map_id not in self.ids.taken_ids("Map"), map_id
            self.ids.taken_ids("Map").add(map_id)
            base = common.OVERLAYS.get(map_id, map_id)
            self.out.add("Map", {
                "ID": map_id, "Directory": directory, "InstanceType": 0, "Flags": stock_flags, "PVP": 0,
                # (the terrain swaps are shown as their base map: the game names a map by its own name)
                "MapName_lang": cata[base]["MapName_lang"], "AreaTableID": 0,
                "LoadingScreenID": self.loading_screen(cata[base]["LoadingScreenID"]),
                "MinimapIconScale": 1.0, "CorpseMapID": -1, "Corpse_0": 0.0, "Corpse_1": 0.0,
                "TimeOfDayOverride": -1, "ExpansionID": 0, "RaidOffset": 0, "MaxPlayers": 0})

    def areas(self):
        rows = [r for r in self.table("AreaTable") if int(r["ContinentID"]) in common.MAPS]
        stock_bits = {r[3] for r in self.ids.stock_rows("AreaTable").values()}
        free_bits = [b for b in FREE_AREA_BITS if b not in stock_bits]
        for r in sorted(rows, key=lambda r: int(r["ID"])):
            area = int(r["ID"])
            assert area not in self.ids.taken_ids("AreaTable"), area
            self.ids.taken_ids("AreaTable").add(area)
            bit = int(r["AreaBit"])
            if bit >= 4096 or bit in stock_bits:
                bit = free_bits.pop(0)
            stock_bits.add(bit)
            flags = int(r["Flags_0"]) & ~AREA_FLAGS_DROPPED & 0xFFFFFFFF
            self.out.add("AreaTable", {
                "ID": area, "ContinentID": int(r["ContinentID"]), "ParentAreaID": int(r["ParentAreaID"]),
                "AreaBit": bit, "Flags": flags,
                "SoundProviderPref": self.provider(r["SoundProviderPref"]),
                "SoundProviderPrefUnderwater": self.provider(r["SoundProviderPrefUnderwater"]),
                "AmbienceID": self.ambience(r["AmbienceID"]), "ZoneMusic": self.music(r["ZoneMusic"]),
                "IntroSound": self.intro(r["IntroSound"]), "ExplorationLevel": int(r["ExplorationLevel"]),
                "AreaName_lang": r["AreaName_lang"], "FactionGroupMask": int(r["FactionGroupMask"]),
                "MinElevation": -500.0, "Ambient_multiplier": float(r["Ambient_multiplier"]), "LightID": 0})

    def wmo_areas(self, wmo_ids):
        """The names, music and ambience of the areas inside the maps' buildings ([wmo_ids]: each
        building's WMO id, its file's id): only Cataclysm's own buildings'. 3.3.5a's own (the ones it
        has rows for, and the ones whose file Wrath's game has, rows or not) are left as they are:
        a row for one would rename its rooms wherever else it stands in the old world."""
        stock_wmos = {r[1] for r in self.ids.stock_rows("WMOAreaTable").values()}
        wmo_ids = {w for w, fdid in wmo_ids.items() if not common.wrath_has(self.cache, fdid)}
        areas = {int(r["ID"]) for r in self.table("AreaTable") if int(r["ContinentID"]) in common.MAPS}
        for r in self.table("WMOAreaTable"):
            wmo = int(r["WMOID"])
            if wmo not in wmo_ids or wmo in stock_wmos:
                continue
            area = int(r["AreaTableID"])
            self.out.add("WMOAreaTable", {
                "ID": self.ids.new("WMOAreaTable", int(r["ID"])), "WMOID": wmo, "NameSetID": int(r["NameSetID"]),
                "WMOGroupID": int(r["WMOGroupID"]), "SoundProviderPref": self.provider(r["SoundProviderPref"]),
                "SoundProviderPrefUnderwater": self.provider(r["SoundProviderPrefUnderwater"]),
                "AmbienceID": self.ambience(r["AmbienceID"]), "ZoneMusic": self.music(r["ZoneMusic"]),
                "IntroSound": self.intro(r["IntroSound"]), "Flags": int(r["Flags"]),
                "AreaTableID": area if area in areas or area in self.ids.taken_ids("AreaTable") else 0,
                "AreaName_lang": r["AreaName_lang"]})

    # --- Lights -------------------------------------------------------------------------------------

    def skybox(self, cata_id):
        cata_id = int(cata_id)
        if cata_id <= 0:
            return 0
        key = ("LightSkybox", cata_id)
        if key not in self.done:
            r = self.by_id("LightSkybox")[cata_id]
            fdid = int(r["SkyboxFileDataID"])
            if not fdid:
                self.done[key] = 0
                return 0
            model = self.file(fdid, "model")
            name = game_path(re.sub(r"\.m2$", ".mdx", model))
            stock = [s for s in self.ids.stock_rows("LightSkybox").values() if s[1].lower() == name.lower()]
            if stock:
                self.done[key] = stock[0][0]
            else:
                our = self.ids.new("LightSkybox", cata_id)
                self.out.add("LightSkybox", {"ID": our, "Name": name, "Flags": int(r["Flags"]) & 0x3})
                self.done[key] = our
        return self.done[key]

    def light_params(self, cata_id):
        cata_id = int(cata_id)
        if cata_id <= 0:
            return 0
        key = ("LightParams", cata_id)
        if key in self.done:
            return self.done[key]
        r = self.by_id("LightParams")[cata_id]
        our = self.ids.new("LightParams")
        self.done[key] = our
        self.out.add("LightParams", {
            "ID": our, "HighlightSky": int(r["HighlightSky"]), "LightSkyboxID": self.skybox(r["LightSkyboxID"]),
            "CloudTypeID": int(r["CloudTypeID"]), "Glow": float(r["Glow"]),
            "WaterShallowAlpha": float(r["WaterShallowAlpha"]), "WaterDeepAlpha": float(r["WaterDeepAlpha"]),
            "OceanShallowAlpha": float(r["OceanShallowAlpha"]), "OceanDeepAlpha": float(r["OceanDeepAlpha"])})
        data = sorted((d for d in self.table("LightData") if int(d["LightParamID"]) == cata_id),
                      key=lambda d: int(d["Time"]))[:16]
        if not data:
            data = [{c: "0" for c in INT_BANDS + ["Time", "FogEnd", "FogScaler", "CloudDensity"]}]
        times = [int(d["Time"]) for d in data]
        for n, column in enumerate(INT_BANDS):
            values = {"ID": our * 18 - 17 + n, "Num": len(data)}
            for i, (t, d) in enumerate(zip(times, data)):
                values[f"Time_{i}"] = t
                values[f"Data_{i}"] = int(d[column]) & 0xFFFFFF       # (3.3.5a's colours are 0x00RRGGBB)
            self.ids.taken_ids("LightIntBand").add(values["ID"])
            self.out.add("LightIntBand", values)
        for n, column in enumerate(FLOAT_BANDS):
            values = {"ID": our * 6 - 5 + n, "Num": len(data)}
            for i, (t, d) in enumerate(zip(times, data)):
                values[f"Time_{i}"] = t
                values[f"Data_{i}"] = float(d[column]) if column else FLOAT_BAND_DEFAULTS[n]
            self.out.add("LightFloatBand", values)
        return our

    def lights(self):
        """Every map's lights (3.3.5a finds a place's light by the map it's on: a terrain swap's map gets
        its base's lights, and its own over them)."""
        cata = self.table("Light")
        for map_id in common.MAPS:
            base = common.OVERLAYS.get(map_id)
            rows = [r for r in cata if int(r["ContinentID"]) in ((map_id, base) if base else (map_id,))]

            def is_global(r):
                return all(float(r[f"GameCoords_{i}"]) == 0 for i in range(3))
            if any(is_global(r) and int(r["ContinentID"]) == map_id for r in rows):
                rows = [r for r in rows if not (is_global(r) and int(r["ContinentID"]) != map_id)]
            for r in sorted(rows, key=lambda r: int(r["ID"])):
                x, y, z = light_coords(float(r["GameCoords_0"]), float(r["GameCoords_1"]), float(r["GameCoords_2"]))
                if float(r["GameCoords_0"]) == 0 and float(r["GameCoords_1"]) == 0 and float(r["GameCoords_2"]) == 0:
                    x = y = z = 0.0          # (the map's own light, everywhere the others aren't)
                values = {"ID": self.ids.new("Light", int(r["ID"]) if int(r["ContinentID"]) == map_id else None),
                          "ContinentID": map_id, "GameCoords_0": x, "GameCoords_1": y, "GameCoords_2": z,
                          "GameFalloffStart": float(r["GameFalloffStart"]) * 36,
                          "GameFalloffEnd": float(r["GameFalloffEnd"]) * 36}
                for i in range(8):
                    values[f"LightParamsID_{i}"] = self.light_params(r[f"LightParamsID_{i}"])
                self.out.add("Light", values)

    # --- World maps ---------------------------------------------------------------------------------

    def art_files(self, art_id, area_name):
        """A UiMapArt's 12 tiles (4 across, 3 down) as Interface\\WorldMap\\<name>\\<name><n>.blp."""
        tiles = sorted((t for t in self.table("UiMapArtTile") if int(t["UiMapArtID"]) == art_id and int(t["LayerIndex"]) == 0),
                       key=lambda t: (int(t["RowIndex"]), int(t["ColIndex"])))
        assert len(tiles) == 12, (art_id, len(tiles))
        for n, t in enumerate(tiles, 1):
            self.files[int(t["FileDataID"])] = (f"interface/worldmap/{area_name.lower()}/{area_name.lower()}{n}.blp", "ui")

    def art_name(self, art_id):
        """The folder name Cataclysm's tiles of an art are in (the listfile's)."""
        for t in self.table("UiMapArtTile"):
            if int(t["UiMapArtID"]) == art_id:
                path = self.names.get(int(t["FileDataID"]), "")
                m = re.match(r"interface/worldmap/([^/]+)/", path)
                if m:
                    return m.group(1)
        raise KeyError(f"UiMapArt {art_id}: its tiles have no names")

    def world_maps(self):
        assignments = {int(a["UiMapID"]): a for a in self.table("UiMapAssignment")
                       if int(a["MapID"]) in common.MAPS and int(a["OrderIndex"]) == 0}
        names = {"gilneas": "Gilneas", "gilneascity": "GilneasCity", "thelostisles": "TheLostIsles", "kezan": "Kezan",
                 "gilneas_terrain1": "Gilneas_terrain1", "gilneas_terrain2": "Gilneas_terrain2",
                 "thelostisles_terrain1": "TheLostIsles_terrain1", "thelostisles_terrain2": "TheLostIsles_terrain2"}
        ours = {}
        for ui_map, (zone, arts, parent) in WORLD_MAPS.items():
            a = assignments[ui_map]
            for map_id, art in arts.items():
                folder = self.art_name(art)
                name = names.get(folder, folder)
                self.art_files(art, name)
                our = self.ids.new("WorldMapArea")
                ours[(ui_map, map_id)] = (our, art, name)
                self.out.add("WorldMapArea", {
                    "ID": our, "MapID": map_id, "AreaID": zone, "AreaName": name,
                    "LocLeft": float(a["Region_4"]), "LocRight": float(a["Region_1"]),
                    "LocTop": float(a["Region_3"]), "LocBottom": float(a["Region_0"]),
                    "DisplayMapID": -1, "DefaultDungeonFloor": 0,
                    "ParentWorldMapID": ours[(parent, map_id)][0] if parent and (parent, map_id) in ours else -1})
        # The discovered parts' pictures over them.
        for (ui_map, map_id), (our, art, name) in ours.items():
            for o in self.table("WorldMapOverlay"):
                if int(o["UiMapArtID"]) != art:
                    continue
                tiles = sorted((t for t in self.table("WorldMapOverlayTile") if t["WorldMapOverlayID"] == o["ID"]
                                and int(t["LayerIndex"]) == 0), key=lambda t: (int(t["RowIndex"]), int(t["ColIndex"])))
                if not tiles:
                    continue
                texture = None
                m = re.match(r"interface/worldmap/[^/]+/(.+?)\d+\.blp$", self.names.get(int(tiles[0]["FileDataID"]), ""))
                texture = m.group(1) if m else f"overlay{o['ID']}"
                for n, t in enumerate(tiles, 1):
                    self.files[int(t["FileDataID"])] = (f"interface/worldmap/{name.lower()}/{texture.lower()}{n}.blp", "ui")
                values = {"ID": self.ids.new("WorldMapOverlay"), "MapAreaID": our, "TextureName": texture,
                          "TextureWidth": int(o["TextureWidth"]), "TextureHeight": int(o["TextureHeight"]),
                          "OffsetX": int(o["OffsetX"]), "OffsetY": int(o["OffsetY"]),
                          "HitRectTop": int(o["HitRectTop"]), "HitRectLeft": int(o["HitRectLeft"]),
                          "HitRectBottom": int(o["HitRectBottom"]), "HitRectRight": int(o["HitRectRight"])}
                for i in range(4):
                    values[f"AreaID_{i}"] = int(o[f"AreaID_{i}"])
                self.out.add("WorldMapOverlay", values)


