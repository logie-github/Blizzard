#!/usr/bin/env python3
"""The starting areas whole: their maps' rows in the game's tables (build_tables.py) and their world,
the Cataclysm Preservation Project's (CPP), put in AzerothCore's tables: the creatures and objects of
the two maps, their looks, factions, paths, formations, texts and gossip.

Nothing of 3.3.5a's world is changed: every row is new, in ranges of its own (ENTRY, GUID, PATH, TEXT
plus Cataclysm's id), so they can be taken out whole (zones_world_off.sql) and the game's own world
told apart from them. The game's tables' rows they need (looks, models, factions, sounds) are new rows
too, where 3.3.5a hasn't the same thing already.

    python3 tools/zones/build_world.py CACHE STOCK_DBC WOWDBDEFS LISTFILE CORE_DIR CONVERTER_SRC

The first five as build_tables.py's; CONVERTER_SRC: wotlkconv's src folder at the commit
zones-version.env pins (it's run in-process, for the tables it joins from others). And a local MariaDB with
CPP's world (db.CPP_DB) and AzerothCore's (db.AC_DB): README, The starting areas. Writes what
build_tables.py does, and data/zones/server/zones_world.sql (and zones_world_off.sql).
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_tables  # noqa: E402
import common  # noqa: E402
import db  # noqa: E402
import files  # noqa: E402
from items import ItemsMixin  # noqa: E402
from quests import QuestsMixin  # noqa: E402
from spells import SpellsMixin  # noqa: E402
from vehicles import VehiclesMixin  # noqa: E402
from scripts import KILL_CREDITS, VEHICLES, ScriptsMixin  # noqa: E402
from build_tables import OUT  # noqa: E402

# The starting areas' rows' ranges: ENTRY + Cataclysm's entry (creatures, objects, quests, gossip
# menus, texts, loot), GUID + CPP's guid for a spawn on its map (and a block more for each terrain
# swap's map it's on too), PATH + CPP's path id (waypoints, action lists). Spawns stay under 0xFFFFFF:
# AzerothCore stops the world server when a new spawn's id (one after the highest) would pass it.
ENTRY = 6_000_000
GUID = 10_000_000
GUID_BLOCK = 1_000_000
PATH = 600_000_000
# The tables convert_rows converts whole.
WHOLE_TABLES = {"ItemDisplayInfo"}
# Gilneas's terrain swaps (common.OVERLAYS): a spawn of CPP's on map 654 is on each map of Gilneas
# whose terrain it's seen with (terrainSwapMap -1: all of them).
GILNEAS = (654, 638, 655)
VERIFIED = -15595                     # (the starting areas' rows' own mark: 4.3.4's build, negative, as none of AzerothCore's)
# Cataclysm's phases on the two maps, as 3.3.5a's phase mask's bits (the default, 169, the first:
# AzerothCore's own default phase).
PHASES = [169, 105, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187,
          188, 189, 190, 191, 194, 379, 380, 381, 382, 383, 384]
# Cataclysm's races in 3.3.5a's race masks: the Worgen are 22 there and 12 here, the Goblins 9 both.
# Cataclysm's races as the realm's game has them: the playable ones as they are, the Worgen (22) at
# 12 (mod-worgoblin's), and the races only creatures use where the realm's modules moved them (the
# Skyborne's 13 and 14 to 22 and 23, the allied races' 15 to 18 to 24 to 27, mod-worgoblin's fel orcs
# to 29: their tools/build_data.py, MOVED). A race the game hasn't (Cataclysm's 0, once given to
# Forest Trolls and Naga here) is a look-up it crashes on (crash reports #88, #93, #98, #99: KTC
# Headquarters' Forest Troll servant).
RACES = {r: r for r in range(1, 12)}
RACES.update({12: 29, 13: 22, 14: 23, 15: 24, 16: 25, 17: 26, 18: 27, 19: 19, 20: 20, 21: 21, 22: 12})
# The creatures' races the modules moved (the game's own rows of theirs go with them).
MOVED_RACES = {9: 28, 12: 29, 13: 22, 14: 23, 15: 24, 16: 25, 17: 26, 18: 27}
# 3.3.5a's npcflag, unit_flags2 and creature type flags: Cataclysm's bits past these mean nothing here.
NPCFLAG_MASK = 0x03FFFFFF
UNIT_FLAGS2_MASK = 0x0003FFFF
# NPC item display slots: CDIE's 11 in 3.3.5a's order, by Cataclysm's NpcModelItemSlotDisplayInfo.ItemSlot.
ITEM_SLOTS = 11


def race_mask(mask):
    out = 0
    for race, ours in RACES.items():
        if mask & (1 << (race - 1)):
            out |= 1 << (ours - 1)
    return out


def num(v, default=0):
    if v is None or v == "":
        return default
    return float(v) if "." in v or "e" in v.lower() else int(v)


def sqlv(v):
    if v is None:
        return "NULL"
    if isinstance(v, str):
        return "'" + v.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "") + "'"
    if isinstance(v, float):
        return repr(v)
    return str(v)


MODULE_DATA = os.path.join(os.path.dirname(os.path.dirname(HERE)), "data")


class Looks:
    """What an NPC's look can name and the game has (CharSections' skins, CharHairGeosets' hair styles,
    CharacterFacialHairStyles' facial hair), by race and sex; one it hasn't is a look-up the game
    crashes on."""

    def __init__(self, stock_dir, module_dbc):
        def stock(table):
            return [list(r) for r in common.Dbc(os.path.join(stock_dir, table + ".dbc")).rows()]

        def module(table):
            out = []
            for line in open(os.path.join(module_dbc, table + ".txt"), encoding="utf-8"):
                f = line.rstrip("\n").split("\t")
                if f[0] == "put":
                    out.append([int(x) if x.lstrip("-").isdigit() else x for x in f[1:]])
                elif f[0] == "appendraw":
                    raw = bytes.fromhex(f[1])
                    out.append(list(struct.unpack(f"<{len(raw) // 4}I", raw)))
            return out

        hair, facial, skin = stock("CharHairGeosets"), stock("CharacterFacialHairStyles"), stock("CharSections")
        for r in hair:
            r[1] = MOVED_RACES.get(r[1], r[1])
        for r in facial:
            r[0] = MOVED_RACES.get(r[0], r[0])
        for r in skin:
            r[1] = MOVED_RACES.get(r[1], r[1])
        hair += module("CharHairGeosets")
        facial += module("CharacterFacialHairStyles")
        skin += module("CharSections")
        self.have = {"hair": {}, "facial": {}, "skin": {}}
        for r in hair:
            self.have["hair"].setdefault((r[1], r[2]), set()).add(r[3])
        for r in facial:
            self.have["facial"].setdefault((r[0], r[1]), set()).add(r[2])
        for r in skin:
            if r[3] == 0:
                self.have["skin"].setdefault((r[1], r[2]), set()).add(r[9])

    def pick(self, kind, race, sex, value):
        """[value] if the game has it for the race and sex, else the nearest it has below it (0 if none)."""
        have = self.have[kind].get((race, sex), set())
        if value in have or not have:
            return value
        below = [v for v in have if v < value]
        return max(below) if below else min(have)


class Sql:
    """INSERT statements by table, in the order tables are first written to."""

    def __init__(self):
        self.tables = {}

    def add(self, table, row):
        self.tables.setdefault(table, []).append(row)

    def write(self, path, header):
        out = [header]
        for table, rows in self.tables.items():
            cols = list(rows[0])
            unknown = set(cols) - set(db.column_names(db.AC_DB, table))
            if unknown:
                raise ValueError(f"{table} hasn't the columns {sorted(unknown)} in AzerothCore's world ({db.AC_DB})")
            names = ", ".join(f"`{c}`" for c in cols)
            for i in range(0, len(rows), 250):
                values = ",\n".join("(" + ", ".join(sqlv(r.get(c)) for c in cols) + ")" for r in rows[i:i + 250])
                out.append(f"INSERT INTO `{table}` ({names}) VALUES\n{values};")
        with open(path, "w", newline="\n") as f:
            f.write("\n".join(out) + "\n")


class WorldBuilder(SpellsMixin, ItemsMixin, QuestsMixin, VehiclesMixin, ScriptsMixin, build_tables.Builder):
    ENTRY, GUID, PATH, GILNEAS = ENTRY, GUID, PATH, GILNEAS

    def __init__(self, cache, stock_dir, dbd, listfile, converter_src):
        super().__init__(cache, stock_dir, dbd, listfile)
        self.creature_queue, self.creatures_seen, self.creatures_done = [], set(), set()
        self.equips = {}             # CPP's creature: its equipment ids
        self.spell_ids = {}          # Cataclysm's spell: the realm's (0: not in it)
        self.renamed = {}            # a class quest: (its spell's name, its stand-in's: quests.STAND_INS)
        self.object_queue, self.objects_seen, self.objects_done = [], set(), set()
        self.quest_queue, self.quests_seen = [], set()
        self.paths_needed, self.actionlists_needed, self.actionlists_done, self.smart_done = set(), set(), set(), set()
        self.spell_hooks, self.aliases, self.ai_templates = [], {}, []
        self.stock_dir, self.dbd, self.converter_src = stock_dir, dbd, converter_src
        self.sql = Sql()
        self.dropped = {}            # what's left out for now, by kind: {kind: set of Cataclysm ids}
        self.world_files = {}        # fdid: (path, kind)
        self.converted = {}          # table: {id: row as values}
        self.tried = {}              # table: ids asked of the converter (once each)
        self.cpp_spawns = db.rows(db.CPP_DB, "SELECT * FROM creature WHERE map IN (654, 648)")
        self.cpp_objects = db.rows(db.CPP_DB, "SELECT * FROM gameobject WHERE map IN (654, 648)")
        self.creatures = {int(r["id"]) for r in self.cpp_spawns}
        self.objects = {int(r["id"]) for r in self.cpp_objects}

    def drop(self, kind, value):
        self.dropped.setdefault(kind, set()).add(int(value))

    # --- Cataclysm's tables through the converter -------------------------------------------------

    def db2(self, name):
        """Cataclysm Classic's .db2 of a table (for the converter, which joins them itself)."""
        folder = os.path.join(self.cache, "db2")
        path = os.path.join(folder, name.lower() + ".db2")
        if not os.path.exists(path):
            fdid = self.fdids.get(f"dbfilesclient/{name.lower()}.db2")
            if fdid is None:
                raise KeyError(f"{name}.db2 isn't in the listfile")
            data = common.file_bytes(self.cache, fdid)
            os.makedirs(folder, exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)
        return path

    def convert_rows(self, name, ids):
        """Cataclysm's rows of [ids] of a table, in 3.3.5a's layout (wotlkconv db convert): {id: values}.
        Item looks are converted whole, once (as quick as one of them: the table's read either way)."""
        if name in WHOLE_TABLES:
            if name not in self.converted:
                self.convert_table(name, ())
        else:
            tried = self.tried.setdefault(name, set())
            want = sorted({int(i) for i in ids if int(i) > 0} - tried)
            tried.update(want)
            if want:
                self.convert_table(name, want)
        return {i: self.converted[name][i] for i in ids if i in self.converted.get(name, {})}

    def convert_table(self, name, ids):
        """convert_rows's conversion: [ids] of a table (() for all of it) into self.converted."""
        work = os.path.join(self.cache, "dbcout")
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work)
        target = os.path.join(work, name + ".dbc")
        self.convert_in_process(name, ids, target)
        got = self.converted.setdefault(name, {})
        for row in common.Dbc(target, common.layout(self.dbd, name)).rows():
            got[row[0]] = row

    def convert_in_process(self, name, ids, target):
        """What `wotlkconv db convert TABLE --only-id ...` does, in-process: the listfile read once, and
        Cataclysm Classic's tables beside it for the columns it joins from others (ItemDisplayInfo's,
        which its command line can't read)."""
        resolver = self.resolver()
        from wotlkconv.db import MappingLibrary, convert_db2, find_template
        from wotlkconv.options import Options
        from wotlkconv.report import FileResult
        opts = Options(db_templates=self.stock_dir, db_merge=False, db_row_ids=tuple(ids), overwrite=True)
        path = self.db2(name)
        result = FileResult(source=path, kind="db2")
        data, result = convert_db2(open(path, "rb").read(), path, opts, resolver.listfile, resolver.tables.definitions,
                                   MappingLibrary(None), find_template(self.stock_dir, name), name, result,
                                   tables=resolver.tables)
        if not result.ok or not data:
            raise RuntimeError(f"{name}: " + "; ".join(n.message for n in result.notes))
        with open(target, "wb") as f:
            f.write(data)

    def columns(self, table):
        return [c for c, _ in common.layout(self.dbd, table)]

    def as_dict(self, table, row):
        return dict(zip(self.columns(table), row))

    def put(self, table, values):
        """A converted row (by column) as a row of ours."""
        self.out.add(table, {k: v for k, v in values.items() if "#" not in k or k.endswith("#flags")})

    def add_file(self, fdid, kind="model"):
        fdid = int(fdid)
        if fdid and fdid in self.names:
            self.world_files[fdid] = (self.names[fdid], kind)

    # --- Looks --------------------------------------------------------------------------------------

    def same_display(self, ours, stock, stock_models, ours_model_path):
        if stock is None:
            return False
        model = stock_models.get(stock[1])
        same_model = model is not None and model[2].lower().replace(".mdx", ".m2") == ours_model_path.lower().replace(".mdx", ".m2")
        same_textures = [t.lower() for t in stock[6:9]] == [t.lower() for t in ours[6:9]]
        return same_model and same_textures and abs(stock[4] - ours[4]) < 1e-4

    def model(self, cata_id):
        """A CreatureModelData of Cataclysm's as one of ours: 3.3.5a's with the same model file, or new."""
        key = ("CreatureModelData", cata_id)
        if key in self.done:
            return self.done[key]
        row = self.convert_rows("CreatureModelData", [cata_id]).get(cata_id)
        if row is None:
            self.done[key] = 0
            return 0
        values = self.as_dict("CreatureModelData", row)
        path = values["ModelName"]
        stock = [r for r in self.stock_models().values() if r[2].lower().replace(".mdx", ".m2") == path.lower().replace(".mdx", ".m2")]
        if stock:
            self.done[key] = stock[0][0]
            return stock[0][0]
        cmd = self.by_id("CreatureModelData").get(cata_id)
        if cmd:
            self.add_file(cmd["FileDataID"])
        values["ID"] = self.ids.new("CreatureModelData", cata_id)
        values["SoundID"] = self.creature_sounds(values.get("SoundID", 0))
        self.put("CreatureModelData", values)
        self.done[key] = values["ID"]
        return values["ID"]

    def stock_models(self):
        if not hasattr(self, "_stock_models"):
            self._stock_models = self.ids.stock_rows("CreatureModelData")
        return self._stock_models

    def creature_sounds(self, cata_id):
        """A CreatureSoundData: 3.3.5a's of that id (they're kept by creature, unchanged), or new."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        if cata_id in self.ids.stock_rows("CreatureSoundData"):
            return cata_id
        key = ("CreatureSoundData", cata_id)
        if key in self.done:
            return self.done[key]
        r = self.by_id("CreatureSoundData").get(cata_id)
        if r is None:
            return 0
        values = {}
        for col, kind in common.layout(self.dbd, "CreatureSoundData"):
            if col == "ID" or col not in r:
                continue
            if kind == "f":
                values[col] = float(r[col])
            elif col.startswith("Sound") or col.startswith("CustomAttack") or col.endswith("SoundID"):
                values[col] = self.sound(r[col])
            elif col.startswith("CreatureSoundDataIDPet"):
                values[col] = 0
            else:
                values[col] = int(float(r[col]))
        values["ID"] = self.ids.new("CreatureSoundData", cata_id)
        self.out.add("CreatureSoundData", values)
        self.done[key] = values["ID"]
        return values["ID"]

    def display(self, cata_id):
        """A CreatureDisplayInfo of Cataclysm's as one of ours: 3.3.5a's own when it's the same look
        (the same model, textures and scale), or new (and its model, its NPC's look, its files)."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = ("CreatureDisplayInfo", cata_id)
        if key in self.done:
            return self.done[key]
        row = self.convert_rows("CreatureDisplayInfo", [cata_id]).get(cata_id)
        if row is None:
            self.drop("display", cata_id)
            self.done[key] = 0
            return 0
        values = self.as_dict("CreatureDisplayInfo", row)
        cmd = self.convert_rows("CreatureModelData", [values["ModelID"]]).get(values["ModelID"])
        path = self.as_dict("CreatureModelData", cmd)["ModelName"] if cmd else ""
        stock = self.ids.stock_rows("CreatureDisplayInfo").get(cata_id)
        if self.same_display(row, stock, self.stock_models(), path):
            self.done[key] = cata_id
            # (one of 3.3.5a's the core's own table hasn't)
            if not db.rows(db.AC_DB, f"SELECT DisplayID FROM creature_model_info WHERE DisplayID = {cata_id}"):
                self.model_info(cata_id, cata_id)
            return cata_id
        values["ID"] = self.ids.new("CreatureDisplayInfo", cata_id)
        self.done[key] = values["ID"]
        values["ModelID"] = self.model(values["ModelID"])
        values["SoundID"] = self.creature_sounds(values["SoundID"])
        values["ExtendedDisplayInfoID"] = self.npc_look(values["ExtendedDisplayInfoID"])
        values["NPCSoundID"] = self.npc_sounds(values["NPCSoundID"])
        values["ParticleColorID"] = 0
        values["ObjectEffectPackageID"] = 0
        cdi = self.by_id("CreatureDisplayInfo").get(cata_id, {})
        for i in range(4):
            self.add_file(cdi.get(f"TextureVariationFileDataID_{i}", 0), "texture")
        self.put("CreatureDisplayInfo", values)
        self.model_info(cata_id, values["ID"])
        return values["ID"]

    def model_info(self, cata_id, our):
        """A new display's creature_model_info (its size, reach and gender), the CPP's: the world
        server loads no creature whose display hasn't one."""
        info = db.rows(db.CPP_DB, f"SELECT * FROM creature_model_info WHERE DisplayID = {int(cata_id)}")
        info = info[0] if info else {"BoundingRadius": 0.306, "CombatReach": 1.5, "Gender": 2, "DisplayID_Other_Gender": 0}
        row = {"DisplayID": our, "BoundingRadius": float(info["BoundingRadius"]), "CombatReach": float(info["CombatReach"]),
               "Gender": num(info["Gender"]), "DisplayID_Other_Gender": 0, "VerifiedBuild": VERIFIED}
        self.sql.add("creature_model_info", row)
        other = num(info["DisplayID_Other_Gender"])
        if other and other != int(cata_id):
            row["DisplayID_Other_Gender"] = self.display(other)

    def npc_sounds(self, cata_id):
        cata_id = int(cata_id or 0)
        if cata_id <= 0 or cata_id in self.ids.stock_rows("NPCSounds"):
            return cata_id
        key = ("NPCSounds", cata_id)
        if key not in self.done:
            r = self.by_id("NPCSounds").get(cata_id)
            if r is None:
                self.done[key] = 0
            else:
                values = {"ID": self.ids.new("NPCSounds", cata_id)}
                for i in range(4):
                    values[f"SoundID_{i}"] = self.sound(r.get(f"SoundID_{i}", 0))
                self.out.add("NPCSounds", values)
                self.done[key] = values["ID"]
        return self.done[key]

    def npc_look(self, cata_id):
        """A CreatureDisplayInfoExtra (a humanoid NPC's look: race, sex, skin, face, hair, its clothes'
        displays and its baked texture), in 3.3.5a's layout (the Worgen 12 here)."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = ("CreatureDisplayInfoExtra", cata_id)
        if key in self.done:
            return self.done[key]
        r = self.by_id("CreatureDisplayInfoExtra").get(cata_id)
        if r is None:
            self.done[key] = 0
            return 0
        race = RACES.get(int(r["DisplayRaceID"]))
        sex = int(r["DisplaySexID"])
        if race is None:
            self.drop("npc look's race", int(r["DisplayRaceID"]))
            self.done[key] = 0
            return 0
        looks = self.looks()
        values = {"ID": self.ids.new("CreatureDisplayInfoExtra", cata_id), "DisplayRaceID": race,
                  "DisplaySexID": sex, "SkinID": looks.pick("skin", race, sex, int(r["SkinID"])),
                  "FaceID": int(r["FaceID"]), "HairStyleID": looks.pick("hair", race, sex, int(r["HairStyleID"])),
                  "HairColorID": int(r["HairColorID"]),
                  "FacialHairID": looks.pick("facial", race, sex, int(r["FacialHairID"])),
                  "Flags": int(r.get("Flags", 0)) & 0x3}
        for slot in self.slots().get(cata_id, {}).items():
            index, item_display = slot
            if 0 <= index < ITEM_SLOTS:
                values[f"NPCItemDisplay_{index}"] = self.item_look(item_display)
        bake = int(r.get("BakeMaterialResourcesID", 0) or 0)
        if bake:
            texture = self.material_file(bake)
            if texture:
                self.add_file(texture, "texture")
                values["BakeName"] = os.path.basename(self.names[texture])
        self.out.add("CreatureDisplayInfoExtra", values)
        self.done[key] = values["ID"]
        return values["ID"]

    def looks(self):
        """The skins, hair styles and facial hair the realm's game has for each race and sex (3.3.5a's
        own, their races moved as the modules move them, and mod-worgoblin's: data/client/dbc)."""
        if not hasattr(self, "_looks"):
            self._looks = Looks(self.stock_dir, os.path.join(MODULE_DATA, "client", "dbc"))
        return self._looks

    def slots(self):
        if not hasattr(self, "_slots"):
            self._slots = {}
            for r in self.table("NpcModelItemSlotDisplayInfo"):
                self._slots.setdefault(int(r["NpcModelID"]), {})[int(r["ItemSlot"])] = int(r["ItemDisplayInfoID"])
        return self._slots

    def material_file(self, material):
        if not hasattr(self, "_materials"):
            self._materials = {}
            for r in self.table("TextureFileData"):
                self._materials.setdefault(int(r["MaterialResourcesID"]), int(r["FileDataID"]))
        return self._materials.get(int(material))

    # --- Factions ----------------------------------------------------------------------------------

    def faction(self, cata_id):
        """A Faction: 3.3.5a's of that id when it's the same one (its name), else new, with a free
        reputation index if it has one and its race masks in 3.3.5a's races."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return cata_id
        stock = self.ids.stock_rows("Faction").get(cata_id)
        r = self.by_id("Faction").get(cata_id)
        if r is None or (stock is not None and stock[23] == r["Name_lang"]):
            return cata_id
        key = ("Faction", cata_id)
        if key in self.done:
            return self.done[key]
        index = int(r["ReputationIndex"])
        if index >= 0:
            used = {s[1] for s in self.ids.stock_rows("Faction").values()} | getattr(self, "_rep_used", set())
            index = next(i for i in range(128) if i not in used)
            self._rep_used = getattr(self, "_rep_used", set()) | {index}
        values = {"ID": self.ids.new("Faction", cata_id), "ReputationIndex": index,
                  "ParentFactionID": self.faction(r["ParentFactionID"]), "Name_lang": r["Name_lang"],
                  "Description_lang": r["Description_lang"]}
        for i in range(4):
            values[f"ReputationRaceMask_{i}"] = race_mask(int(r[f"ReputationRaceMask_{i}"]) & 0xFFFFFFFF)
            values[f"ReputationClassMask_{i}"] = int(r[f"ReputationClassMask_{i}"])
            values[f"ReputationBase_{i}"] = int(r[f"ReputationBase_{i}"])
            values[f"ReputationFlags_{i}"] = int(r[f"ReputationFlags_{i}"])
        for i in range(2):
            values[f"ParentFactionMod_{i}"] = float(r[f"ParentFactionMod_{i}"])
            values[f"ParentFactionCap_{i}"] = int(r[f"ParentFactionCap_{i}"])
        self.done[key] = values["ID"]
        self.out.add("Faction", values)
        return values["ID"]

    def faction_template(self, cata_id):
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return cata_id
        key = ("FactionTemplate", cata_id)
        if key in self.done:
            return self.done[key]
        r = self.by_id("FactionTemplate").get(cata_id)
        if r is None:
            self.drop("faction template", cata_id)
            return 35                             # (friendly to all, as AzerothCore's default)
        values = {"Faction": self.faction(r["Faction"]), "Flags": int(r["Flags"]), "FactionGroup": int(r["FactionGroup"]),
                  "FriendGroup": int(r["FriendGroup"]), "EnemyGroup": int(r["EnemyGroup"])}
        for i in range(4):
            values[f"Enemies_{i}"] = self.faction(r[f"Enemies_{i}"])
            values[f"Friend_{i}"] = self.faction(r[f"Friend_{i}"])
        stock = self.ids.stock_rows("FactionTemplate").get(cata_id)
        if stock is not None and stock[1:5] == [values["Faction"], values["Flags"], values["FactionGroup"], values["FriendGroup"]]:
            self.done[key] = cata_id
            return cata_id
        values["ID"] = self.ids.new("FactionTemplate", cata_id)
        self.out.add("FactionTemplate", values)
        self.done[key] = values["ID"]
        return values["ID"]

    # --- Creatures ---------------------------------------------------------------------------------

    def phase_mask(self, phase_id, phase_group):
        phase_id, phase_group = int(phase_id or 0), int(phase_group or 0)
        phases = [phase_id] if phase_id else self.phase_groups().get(phase_group, [])
        mask = 0
        for p in phases:
            if p in PHASES:
                mask |= 1 << PHASES.index(p)
            else:
                self.drop("phase", p)
        return mask or 1

    def phase_groups(self):
        if not hasattr(self, "_groups"):
            self._groups = {}
            for r in self.table("PhaseXPhaseGroup"):
                self._groups.setdefault(int(r["PhaseGroupID"]), []).append(int(r["PhaseID"]))
        return self._groups

    def creature_entry(self, cata_entry):
        cata_entry = int(cata_entry or 0)
        return ENTRY + cata_entry if cata_entry else 0

    def object_entry(self, cata_entry):
        cata_entry = int(cata_entry or 0)
        return ENTRY + cata_entry if cata_entry else 0

    def need_creature(self, cata_entry):
        cata_entry = int(cata_entry or 0)
        if cata_entry > 0 and cata_entry not in self.creatures_seen:
            self.creatures_seen.add(cata_entry)
            self.creature_queue.append(cata_entry)

    def need_object(self, cata_entry):
        cata_entry = int(cata_entry or 0)
        if cata_entry > 0 and cata_entry not in self.objects_seen:
            self.objects_seen.add(cata_entry)
            self.object_queue.append(cata_entry)

    def creatures_templates(self, batch):
        templates = {int(r["entry"]): r for r in db.rows(db.CPP_DB, f"SELECT * FROM creature_template WHERE entry IN ({db.ids_in(batch)})")}
        for e in set(batch) - set(templates):
            self.drop("creature (not in CPP)", e)
        for t in templates.values():
            for k in ("KillCredit1", "KillCredit2"):
                self.need_creature(t[k])
        entries = set(templates)
        self.creatures_done |= entries
        models = db.rows(db.CPP_DB, f"SELECT * FROM creature_template_model WHERE CreatureID IN ({db.ids_in(entries)})")
        gossip = {int(r["CreatureID"]): int(r["MenuID"]) for r in db.rows(db.CPP_DB, f"SELECT * FROM creature_template_gossip WHERE CreatureID IN ({db.ids_in(entries)})")}
        movement = {int(r["CreatureId"]): r for r in db.rows(db.CPP_DB, f"SELECT * FROM creature_template_movement WHERE CreatureId IN ({db.ids_in(entries)})")}
        addons = {int(r["entry"]): r for r in db.rows(db.CPP_DB, f"SELECT * FROM creature_template_addon WHERE entry IN ({db.ids_in(entries)})")}
        spells = db.rows(db.CPP_DB, f"SELECT entry, spell1, spell2, spell3, spell4, spell5, spell6, spell7, spell8 FROM creature_template WHERE entry IN ({db.ids_in(entries)})")
        for r in spells:
            for i in range(1, 9):
                spell = self.spell(r[f"spell{i}"])
                if spell:
                    self.sql.add("creature_template_spell", {"CreatureID": ENTRY + int(r["entry"]), "Index": i - 1, "Spell": spell, "VerifiedBuild": VERIFIED})
        for e, t in sorted(templates.items()):
            self.sql.add("creature_template", {
                "entry": ENTRY + e, "difficulty_entry_1": 0, "difficulty_entry_2": 0, "difficulty_entry_3": 0,
                "KillCredit1": self.creature_entry(int(t["KillCredit1"]) or KILL_CREDITS.get(e, 0)), "KillCredit2": self.creature_entry(t["KillCredit2"]),
                "name": t["name"], "subname": t["subname"], "IconName": t["IconName"],
                "gossip_menu_id": self.gossip_menu(gossip.get(e, 0)), "minlevel": num(t["minlevel"]), "maxlevel": num(t["maxlevel"]),
                "exp": 0, "faction": self.faction_template(t["faction"]), "npcflag": num(t["npcflag"]) & NPCFLAG_MASK,
                "speed_walk": num(t["speed_walk"]), "speed_run": num(t["speed_run"]), "speed_swim": 1.0, "speed_flight": 1.0,
                "detection_range": 20.0, "rank": num(t["rank"]), "dmgschool": num(t["dmgschool"]),
                "DamageModifier": num(t["DamageModifier"]), "BaseAttackTime": num(t["BaseAttackTime"]),
                "RangeAttackTime": num(t["RangeAttackTime"]), "BaseVariance": num(t["BaseVariance"]),
                "RangeVariance": num(t["RangeVariance"]), "unit_class": num(t["unit_class"]), "unit_flags": num(t["unit_flags"]),
                "unit_flags2": num(t["unit_flags2"]) & UNIT_FLAGS2_MASK, "dynamicflags": 0, "family": num(t["family"]),
                "type": num(t["type"]), "type_flags": num(t["type_flags"]),
                "lootid": self.loot("creature_loot_template", t["lootid"]),
                "pickpocketloot": self.loot("pickpocketing_loot_template", t["pickpocketloot"]),
                "skinloot": self.loot("skinning_loot_template", t["skinloot"]), "PetSpellDataId": 0, "VehicleId": self.vehicle(int(t["VehicleId"]) or VEHICLES.get(e, 0)),
                "mingold": num(t["mingold"]), "maxgold": num(t["maxgold"]), "AIName": "",
                "MovementType": num(t["MovementType"]), "HoverHeight": num(t["HoverHeight"]),
                "HealthModifier": num(t["HealthModifier"]), "ManaModifier": num(t["ManaModifier"]),
                "ArmorModifier": num(t["ArmorModifier"]), "ExperienceModifier": num(t["ExperienceModifier"]),
                "RacialLeader": num(t["RacialLeader"]), "movementId": 0, "RegenHealth": num(t["RegenHealth"]),
                "CreatureImmunitiesId": 0, "flags_extra": 0, "ScriptName": self.script_name(t["ScriptName"], "creature", e),
                "VerifiedBuild": VERIFIED})
            if t["AIName"] == "SmartAI":
                self.ai_templates.append(self.sql.tables["creature_template"][-1])
        for m in models:
            display = self.display(m["CreatureDisplayID"])
            if display:
                self.sql.add("creature_template_model", {
                    "CreatureID": ENTRY + int(m["CreatureID"]), "Idx": num(m["Idx"]), "CreatureDisplayID": display,
                    "DisplayScale": 1.0, "Probability": num(m["Probability"]) or 1.0, "VerifiedBuild": VERIFIED})
        for e, mv in sorted(movement.items()):
            self.sql.add("creature_template_movement", {
                "CreatureId": ENTRY + e, "Ground": 1, "Swim": 1, "Flight": 1 if num(mv["GravityInitiallyDisabled"]) else 0,
                "Rooted": 0, "Chase": 0, "Random": num(mv["Random"]), "InteractionPauseTimer": num(mv["InteractionPauseTimer"])})
        for e, a in sorted(addons.items()):
            self.sql.add("creature_template_addon", self.addon(a, "entry", ENTRY + e))
        self.trainers(entries)
        self.equipment(entries)
        self.vehicle_riders(entries)
        return templates

    def equipment(self, entries):
        """Their weapons (creature_equip_template: items, which 3.3.5a shows by their Item rows)."""
        for r in db.rows(db.CPP_DB, f"SELECT * FROM creature_equip_template WHERE CreatureID IN ({db.ids_in(entries)})"):
            items = [self.item(r[f"ItemID{i}"]) for i in (1, 2, 3)]
            self.equips.setdefault(int(r["CreatureID"]), set()).add(int(r["ID"]))
            self.sql.add("creature_equip_template", {"CreatureID": ENTRY + int(r["CreatureID"]), "ID": r["ID"],
                                                     "ItemID1": items[0], "ItemID2": items[1], "ItemID3": items[2],
                                                     "VerifiedBuild": VERIFIED})

    def addon(self, a, key, value):
        auras = " ".join(str(s) for s in (self.spell(x) for x in (a.get("auras") or "").split()) if s)
        return {key: value, "path_id": PATH + num(a["waypointPathId"]) if num(a["waypointPathId"]) else 0,
                "mount": self.display(a["mount"]),
                "bytes1": num(a["StandState"]) | (num(a["VisFlags"]) << 16) | (num(a["AnimTier"]) << 24),
                "bytes2": num(a["SheathState"]) | (num(a["PvPFlags"]) << 8),
                "emote": num(a["emote"]), "visibilityDistanceType": num(a["visibilityDistanceType"]), "auras": auras or None}

    def equipment_id(self, spawn):
        """A spawn's equipment: CPP's 0 is its creature's first (AzerothCore's 0 is none)."""
        ids = self.equips.get(int(spawn["id"]), set())
        wanted = num(spawn["equipment_id"])
        if wanted == 0:
            return 1 if 1 in ids else 0
        return wanted if wanted == -1 or wanted in ids else 0

    def spawn_maps(self, row):
        """The maps of ours a spawn of CPP's is on (Gilneas's by the terrain it's seen with)."""
        if int(row["map"]) != 654:
            return [int(row["map"])]
        swap = int(row["terrainSwapMap"])
        return list(GILNEAS) if swap == -1 else [swap]

    def spawn_guid(self, guid, map_id):
        block = GILNEAS.index(map_id) if map_id in GILNEAS else 0
        return GUID + block * GUID_BLOCK + int(guid)

    def creature_spawns(self):
        addons = {int(r["guid"]): r for r in db.rows(db.CPP_DB, "SELECT a.* FROM creature_addon a JOIN creature c ON c.guid = a.guid WHERE c.map IN (654, 648)")}
        paths = set()
        for r in self.cpp_spawns:
            for map_id in self.spawn_maps(r):
                guid = self.spawn_guid(r["guid"], map_id)
                self.sql.add("creature", {
                    "guid": guid, "id": ENTRY + int(r["id"]), "map": map_id, "zoneId": 0, "areaId": 0, "spawnMask": 1,
                    "phaseMask": self.phase_mask(r["PhaseId"], r["PhaseGroup"]), "equipment_id": self.equipment_id(r),
                    "position_x": num(r["position_x"]), "position_y": num(r["position_y"]), "position_z": num(r["position_z"]),
                    "orientation": num(r["orientation"]), "spawntimesecs": num(r["spawntimesecs"]),
                    "wander_distance": num(r["wander_distance"]), "currentwaypoint": 0, "curhealth": num(r["curhealth"]),
                    "curmana": num(r["curmana"]), "MovementType": num(r["MovementType"]), "npcflag": num(r["npcflag"]) & NPCFLAG_MASK,
                    "unit_flags": num(r["unit_flags"]), "dynamicflags": 0,
                    "ScriptName": self.script_name(r.get("ScriptName"), "creature spawn", int(r["guid"])), "VerifiedBuild": VERIFIED,
                    "CreateObject": 0, "Comment": None})
                a = addons.get(int(r["guid"]))
                if a:
                    row = self.addon(a, "guid", guid)
                    self.sql.add("creature_addon", row)
                    if num(a["waypointPathId"]):
                        paths.add(int(a["waypointPathId"]))
        return paths

    def waypoints(self, paths):
        for r in db.rows(db.CPP_DB, f"SELECT * FROM waypoint_data WHERE id IN ({db.ids_in(paths)}) ORDER BY id, point"):
            self.sql.add("waypoint_data", {
                "id": PATH + int(r["id"]), "point": num(r["point"]), "position_x": num(r["position_x"]),
                "position_y": num(r["position_y"]), "position_z": num(r["position_z"]), "orientation": num(r["orientation"]) if r["orientation"] else None,
                "velocity": num(r["velocity"]), "delay": num(r["delay"]), "smoothTransition": num(r["smoothTransition"]),
                "move_type": num(r["move_type"]), "action": 0, "action_chance": 100, "wpguid": 0})

    def formations(self):
        guids = {int(r["guid"]): r for r in self.cpp_spawns}
        for r in db.rows(db.CPP_DB, f"SELECT * FROM creature_formations WHERE LeaderGUID IN ({db.ids_in(guids)})"):
            leader = guids.get(int(r["LeaderGUID"]))
            member = guids.get(int(r["MemberGUID"]))
            if not leader or not member:
                continue
            for map_id in set(self.spawn_maps(leader)) & set(self.spawn_maps(member)):
                self.sql.add("creature_formations", {
                    "leaderGUID": self.spawn_guid(r["LeaderGUID"], map_id), "memberGUID": self.spawn_guid(r["MemberGUID"], map_id),
                    "dist": num(r["FollowDistance"]), "angle": num(r["FollowAngle"]), "groupAI": num(r["GroupAI"]),
                    "point_1": max(0, num(r["InversionPoint1"])), "point_2": max(0, num(r["InversionPoint2"]))})   # (-1, none: 0 here)

    # --- Texts and gossip --------------------------------------------------------------------------

    def broadcast(self, cata_id):
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = ("broadcast_text", cata_id)
        if key not in self.done:
            rows = db.rows(db.CPP_DB, f"SELECT * FROM broadcast_text WHERE ID = {cata_id}")
            if not rows:
                self.done[key] = 0
                return 0
            r = rows[0]
            self.sql.add("broadcast_text", {
                "ID": ENTRY + cata_id, "LanguageID": num(r["LanguageID"]), "MaleText": r["Text"], "FemaleText": r["Text1"],
                "EmoteID1": num(r["EmoteID1"]), "EmoteID2": num(r["EmoteID2"]), "EmoteID3": num(r["EmoteID3"]),
                "EmoteDelay1": num(r["EmoteDelay1"]), "EmoteDelay2": num(r["EmoteDelay2"]), "EmoteDelay3": num(r["EmoteDelay3"]),
                "SoundEntriesId": self.sound(r["SoundEntriesID"]), "EmotesID": num(r["EmotesID"]), "Flags": num(r["Flags"]),
                "VerifiedBuild": VERIFIED})
            self.done[key] = ENTRY + cata_id
        return self.done[key]

    def creature_texts(self, entries):
        for r in db.rows(db.CPP_DB, f"SELECT * FROM creature_text WHERE CreatureID IN ({db.ids_in(entries)})"):
            self.sql.add("creature_text", {
                "CreatureID": ENTRY + int(r["CreatureID"]), "GroupID": num(r["GroupID"]), "ID": num(r["ID"]), "Text": r["Text"],
                "Type": num(r["Type"]), "Language": num(r["Language"]), "Probability": num(r["Probability"]),
                "Emote": num(r["Emote"]), "Duration": num(r["Duration"]), "Sound": self.sound(r["Sound"]),
                "BroadcastTextId": self.broadcast(r["BroadcastTextId"]), "TextRange": num(r["TextRange"]), "comment": r["comment"]})

    def npc_text(self, cata_id):
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = ("npc_text", cata_id)
        if key in self.done:
            return self.done[key]
        rows = db.rows(db.CPP_DB, f"SELECT * FROM npc_text WHERE ID = {cata_id}")
        if not rows:
            self.done[key] = 0
            return 0
        r = rows[0]
        values = {"ID": ENTRY + cata_id}
        for i in range(8):
            if f"text{i}_0" not in r:
                break
            values.update({f"text{i}_0": r[f"text{i}_0"], f"text{i}_1": r[f"text{i}_1"],
                           f"BroadcastTextID{i}": self.broadcast(r[f"BroadcastTextID{i}"]), f"lang{i}": num(r[f"lang{i}"]),
                           f"Probability{i}": num(r[f"Probability{i}"])})
            for k in range(3):
                values[f"em{i}_{k * 2}"] = num(r[f"EmoteDelay{i}_{k}"])
                values[f"em{i}_{k * 2 + 1}"] = num(r[f"Emote{i}_{k}"])
        self.sql.add("npc_text", values)
        self.done[key] = ENTRY + cata_id
        return self.done[key]

    def gossip_menu(self, cata_id):
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = ("gossip_menu", cata_id)
        if key in self.done:
            return self.done[key]
        self.done[key] = ENTRY + cata_id
        for r in db.rows(db.CPP_DB, f"SELECT * FROM gossip_menu WHERE MenuID = {cata_id}"):
            self.sql.add("gossip_menu", {"MenuID": ENTRY + cata_id, "TextID": self.npc_text(r["TextID"])})
        for r in db.rows(db.CPP_DB, f"SELECT * FROM gossip_menu_option WHERE MenuID = {cata_id}"):
            self.sql.add("gossip_menu_option", {
                "MenuID": ENTRY + cata_id, "OptionID": num(r["OptionID"]), "OptionIcon": num(r["OptionIcon"]),
                "OptionText": r["OptionText"], "OptionBroadcastTextID": self.broadcast(r["OptionBroadcastTextID"]),
                "OptionType": num(r["OptionType"]), "OptionNpcFlag": num(r["OptionNpcflag"]) & NPCFLAG_MASK,
                "ActionMenuID": self.gossip_menu(r["ActionMenuID"]), "ActionPoiID": 0, "BoxCoded": num(r["BoxCoded"]),
                "BoxMoney": num(r["BoxMoney"]), "BoxText": r["BoxText"], "BoxBroadcastTextID": self.broadcast(r["BoxBroadcastTextID"]),
                "VerifiedBuild": VERIFIED})
        return self.done[key]

    # --- Objects -----------------------------------------------------------------------------------

    def object_display(self, cata_id):
        """A GameObjectDisplayInfo of Cataclysm's as one of ours: 3.3.5a's when it's the same model,
        or new (and its model's files)."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = ("GameObjectDisplayInfo", cata_id)
        if key in self.done:
            return self.done[key]
        row = self.convert_rows("GameObjectDisplayInfo", [cata_id]).get(cata_id)
        if row is None:
            self.drop("object display", cata_id)
            self.done[key] = 0
            return 0
        values = self.as_dict("GameObjectDisplayInfo", row)
        stock = self.ids.stock_rows("GameObjectDisplayInfo").get(cata_id)
        if stock is not None and stock[1].lower().replace(".mdx", ".m2") == values["ModelName"].lower().replace(".mdx", ".m2"):
            self.done[key] = cata_id
            return cata_id
        values["ID"] = self.ids.new("GameObjectDisplayInfo", cata_id)
        for k, v in list(values.items()):
            if k.startswith("Sound_"):
                values[k] = self.sound(v)
        values["ObjectEffectPackageID"] = 0
        god = self.by_id("GameObjectDisplayInfo").get(cata_id)
        if god:
            self.add_file(god["FileDataID"])
        self.put("GameObjectDisplayInfo", values)
        self.done[key] = values["ID"]
        return values["ID"]

    def objects_templates(self, batch):
        templates = db.rows(db.CPP_DB, f"SELECT * FROM gameobject_template WHERE entry IN ({db.ids_in(batch)})")
        addons = {int(r["entry"]): r for r in db.rows(db.CPP_DB, f"SELECT * FROM gameobject_template_addon WHERE entry IN ({db.ids_in(batch)})")}
        self.objects_done |= {int(t["entry"]) for t in templates}
        for t in templates:
            e = int(t["entry"])
            values = {"entry": ENTRY + e, "type": num(t["type"]), "displayId": self.object_display(t["displayId"]),
                      "name": t["name"], "IconName": t["IconName"], "castBarCaption": t["castBarCaption"], "unk1": t["unk1"],
                      "size": num(t["size"])}
            for i in range(24):
                values[f"Data{i}"] = self.object_data(num(t["type"]), i, num(t[f"Data{i}"]), e)
            values.update({"AIName": "", "ScriptName": self.script_name(t["ScriptName"], "object", e), "VerifiedBuild": VERIFIED})
            if t["AIName"] == "SmartGameObjectAI":
                values["AIName"] = "SmartGameObjectAI"
            self.sql.add("gameobject_template", values)
            a = addons.get(e)
            if a:
                self.sql.add("gameobject_template_addon", {
                    "entry": ENTRY + e, "faction": self.faction_template(a["faction"]) if num(a["faction"]) else 0,
                    "flags": num(a["flags"]), "mingold": num(a["mingold"]), "maxgold": num(a["maxgold"]),
                    "artkit0": 0, "artkit1": 0, "artkit2": 0, "artkit3": 0})

    # Each object type's data fields that name something (AzerothCore's layout, CPP's the same for these).
    OBJECT_DATA = {0: {1: "lock"}, 1: {1: "lock", 3: "object"}, 2: {0: "lock", 1: "none", 3: "gossip"},
                   3: {0: "lock", 1: "loot", 6: "event", 7: "object", 8: "quest", 14: "none"}, 5: {5: "quest"},
                   6: {0: "lock", 3: "spell", 12: "none", 13: "none"}, 8: {2: "object", 4: "quest"},
                   10: {0: "lock", 1: "quest", 2: "event", 7: "page", 10: "spell", 12: "object", 14: "none", 15: "none", 19: "gossip"},
                   22: {0: "spell"}}

    def object_data(self, kind, index, value, entry):
        what = self.OBJECT_DATA.get(kind, {}).get(index)
        if not value or what is None:
            return value
        if what == "lock":
            if value in self.ids.stock_rows("Lock"):
                return value
            self.drop("object lock", value)
            return 0
        if what == "loot":
            return self.loot("gameobject_loot_template", value)
        if what == "quest":
            return self.quest_id(value)
        if what == "spell":
            return self.spell(value)
        if what == "object":
            self.need_object(value)
            return self.object_entry(value)
        if what == "gossip":
            return self.gossip_menu(value)
        self.drop(f"object data {what}", entry)
        return 0

    def object_spawns(self):
        addons = {int(r["guid"]): r for r in db.rows(db.CPP_DB, "SELECT a.* FROM gameobject_addon a JOIN gameobject g ON g.guid = a.guid WHERE g.map IN (654, 648)")}
        for r in self.cpp_objects:
            for map_id in self.spawn_maps(r):
                guid = self.spawn_guid(r["guid"], map_id)
                self.sql.add("gameobject", {
                    "guid": guid, "id": ENTRY + int(r["id"]), "map": map_id, "zoneId": 0, "areaId": 0, "spawnMask": 1,
                    "phaseMask": self.phase_mask(r["PhaseId"], r["PhaseGroup"]), "position_x": num(r["position_x"]),
                    "position_y": num(r["position_y"]), "position_z": num(r["position_z"]), "orientation": num(r["orientation"]),
                    "rotation0": num(r["rotation0"]), "rotation1": num(r["rotation1"]), "rotation2": num(r["rotation2"]),
                    "rotation3": num(r["rotation3"]), "spawntimesecs": num(r["spawntimesecs"]), "animprogress": num(r["animprogress"]),
                    "state": num(r["state"]), "ScriptName": self.script_name(r.get("ScriptName"), "object spawn", int(r["guid"])),
                    "VerifiedBuild": VERIFIED, "Comment": None})
                a = addons.get(int(r["guid"]))
                if a:
                    self.sql.add("gameobject_addon", {
                        "guid": guid, "parent_rotation0": num(a["parent_rotation0"]), "parent_rotation1": num(a["parent_rotation1"]),
                        "parent_rotation2": num(a["parent_rotation2"]), "parent_rotation3": num(a["parent_rotation3"]),
                        "invisibilityType": num(a["invisibilityType"]), "invisibilityValue": num(a["invisibilityValue"])})

    # --- The whole of it ---------------------------------------------------------------------------

    def prefetch(self):
        """Every look the creatures and objects have, through the converter at once (each run of it
        reads the whole listfile)."""
        entries = set(self.creatures)
        for t in db.rows(db.CPP_DB, f"SELECT KillCredit1, KillCredit2 FROM creature_template WHERE entry IN ({db.ids_in(entries)})"):
            entries |= {int(t["KillCredit1"]), int(t["KillCredit2"])} - {0}
        displays = {int(r["CreatureDisplayID"]) for r in db.rows(db.CPP_DB, f"SELECT CreatureDisplayID FROM creature_template_model WHERE CreatureID IN ({db.ids_in(entries)})")}
        displays |= {int(r["mount"]) for r in db.rows(db.CPP_DB, f"SELECT mount FROM creature_template_addon WHERE entry IN ({db.ids_in(entries)})")}
        displays |= {int(r["mount"]) for r in db.rows(db.CPP_DB, "SELECT a.mount FROM creature_addon a JOIN creature c ON c.guid = a.guid WHERE c.map IN (654, 648)")}
        rows = self.convert_rows("CreatureDisplayInfo", displays)
        self.convert_rows("CreatureModelData", {r[1] for r in rows.values()})
        objects = {int(r["displayId"]) for r in db.rows(db.CPP_DB, f"SELECT displayId FROM gameobject_template WHERE entry IN ({db.ids_in(self.objects)})")}
        self.convert_rows("GameObjectDisplayInfo", objects)

    def world(self):
        self.prefetch()
        for e in sorted(self.creatures):
            self.need_creature(e)
        for e in sorted(self.objects):
            self.need_object(e)
        self.need_scripted()
        # (creatures, objects, quests and scripts name each other: until nothing new is named)
        while True:
            while self.creature_queue or self.object_queue or self.quest_queue:
                if self.creature_queue:
                    batch, self.creature_queue = self.creature_queue, []
                    self.creatures_templates(batch)
                if self.object_queue:
                    batch, self.object_queue = self.object_queue, []
                    self.objects_templates(batch)
                if self.quest_queue:
                    self.quests()
            new = (self.creatures_done | self.objects_done) - self.smart_done
            if not new:
                break
            self.smart_done |= new
            self.smart_scripts(new)
            if not (self.creature_queue or self.object_queue or self.quest_queue):
                break
        paths = self.creature_spawns()
        self.waypoints(paths | self.paths_needed)
        self.formations()
        self.creature_texts(self.creatures_done)
        self.object_spawns()
        self.quest_relations()
        self.vendors()
        self.graveyards()
        self.area_triggers()
        self.area_spells()
        self.credits = self.cast_credits()


# The columns a starting areas' row is known by, by table (to take exactly their rows out again).
KEYS = {"creature_template": ["entry"], "creature_template_model": ["CreatureID"], "creature_template_movement": ["CreatureId"],
        "creature_template_addon": ["entry"], "creature_template_spell": ["CreatureID"], "creature_text": ["CreatureID"],
        "creature": ["guid"], "creature_addon": ["guid"], "creature_formations": ["memberGUID"], "waypoint_data": ["id"],
        "broadcast_text": ["ID"], "npc_text": ["ID"], "gossip_menu": ["MenuID"], "gossip_menu_option": ["MenuID"],
        "gameobject_template": ["entry"], "gameobject_template_addon": ["entry"], "gameobject": ["guid"], "gameobject_addon": ["guid"],
        "item_template": ["entry"], "quest_template": ["ID"], "quest_template_addon": ["ID"], "quest_offer_reward": ["ID"],
        "quest_request_items": ["ID"], "quest_details": ["ID"], "quest_poi": ["QuestID"], "quest_poi_points": ["QuestID"],
        "creature_queststarter": ["id", "quest"], "creature_questender": ["id", "quest"], "gameobject_queststarter": ["id", "quest"],
        "gameobject_questender": ["id", "quest"], "smart_scripts": ["entryorguid", "source_type"],
        "creature_loot_template": ["Entry"], "pickpocketing_loot_template": ["Entry"], "skinning_loot_template": ["Entry"],
        "reference_loot_template": ["Entry"], "gameobject_loot_template": ["Entry"], "npc_vendor": ["entry"],
        "spell_script_names": ["spell_id", "ScriptName"], "spell_target_position": ["ID", "EffectIndex"],
        "vehicle_template_accessory": ["entry"], "npc_spellclick_spells": ["npc_entry"],
        "creature_default_trainer": ["CreatureId"], "creature_equip_template": ["CreatureID"], "game_graveyard": ["ID"], "graveyard_zone": ["ID", "GhostZone"],
        "areatrigger": ["entry"], "areatrigger_involvedrelation": ["id"], "areatrigger_scripts": ["entry"],
        "spell_area": ["spell", "area"], "creature_model_info": ["DisplayID"], "conditions": ["SourceTypeOrReferenceId", "SourceGroup", "SourceEntry"]}


def write_world(b):
    server = os.path.join(OUT, "server")
    b.sql.write(os.path.join(server, "zones_world.sql"),
                "-- The starting areas' world (tools/zones/build_world.py): the Cataclysm Preservation Project's creatures,\n"
                "-- objects, quests, scripts, loot and the rest of Gilneas and the Lost Isles, in rows of their own (ids from\n"
                "-- 6000000, spawns from 10000000, paths from 600000000; their items keep Cataclysm's ids where they're free).\n"
                "-- Put in by src/WorgenGoblin.cpp with the starting areas on, taken out with them off.")
    with open(os.path.join(server, "zones_world_off.sql"), "w", newline="\n") as f:
        f.write("-- The starting areas' world out (tools/zones/build_world.py): exactly their rows, by their keys.\n")
        for table, rows in b.sql.tables.items():
            keys = KEYS[table]
            values = sorted({tuple(r[k] for k in keys) for r in rows})
            for i in range(0, len(values), 500):
                chunk = values[i:i + 500]
                if len(keys) == 1:
                    f.write(f"DELETE FROM `{table}` WHERE `{keys[0]}` IN ({', '.join(sqlv(v[0]) for v in chunk)});\n")
                else:
                    f.write(f"DELETE FROM `{table}` WHERE ({', '.join(f'`{k}`' for k in keys)}) IN ("
                            + ", ".join("(" + ", ".join(sqlv(x) for x in v) + ")" for v in chunk) + ");\n")
    with open(os.path.join(OUT, "aliases.tsv"), "w", newline="\n") as f:
        f.write("# Other paths the game loads some of the starting areas' files by (tools/zones/build_world.py: an item's\n"
                "# model, textures and icon where 3.3.5a looks for them): id, path\n")
        for fdid, paths in sorted(b.aliases.items()):
            for path in sorted(paths):
                f.write(f"{fdid}\t{path}\n")
    with open(os.path.join(OUT, "spell-hooks.tsv"), "w", newline="\n") as f:
        f.write("# Cataclysm's spell effects and auras 3.3.5a hasn't, made dummies the module answers (tools/zones/spells.py):\n"
                "# Cataclysm's spell id, the spell's id here, effect index, what, Cataclysm's value\n")
        for cata_id, index, what, value in b.spell_hooks:
            f.write(f"{cata_id}\t{b.done.get(('Spell', cata_id), cata_id)}\t{index}\t{what}\t{value}\n")
    with open(os.path.join(OUT, "left-for-later.txt"), "w", newline="\n") as f:
        f.write("# What the starting areas' world names that isn't in it yet (the stages to come: PLAN.md), by kind:\n")
        for kind, ids in sorted(b.dropped.items()):
            f.write(f"{kind}: {len(ids)}: {' '.join(str(i) for i in sorted(ids)[:200])}\n")


def main():
    if len(sys.argv) != 7:
        sys.exit(__doc__)
    cache, stock_dir, dbd, listfile_path, core, converter_src = sys.argv[1:]
    b = WorldBuilder(cache, stock_dir, dbd, listfile_path, converter_src)
    b.listfile_path, b.core = listfile_path, core
    b.maps()
    b.areas()
    b.lights()
    b.world_maps()
    b.world()
    # The two races' intros, Cataclysm's camera flights with their narration.
    for race, cata_seq in build_tables.INTROS_CATACLYSM.items():
        b.out.intros[race] = b.cinematic(cata_seq)
        if b.out.intros[race]:
            b.out.set("ChrRaces", race, build_tables.CHRRACES_CINEMATIC, b.out.intros[race])
    # The maps' files, the world's, and everything they use; the buildings' rooms.
    start = files.map_files(b.names)
    start.update(b.files)
    start.update(b.world_files)
    for fdid in b.aliases:
        start.setdefault(fdid, (b.names[fdid], "texture"))
    found, wmo_ids, missing = files.closure(cache, b.names, b.fdids, start)
    b.wmo_areas(wmo_ids)
    b.out.write(core)
    write_world(b)
    b.write_ids_header(PHASES)
    with open(os.path.join(OUT, "files.tsv"), "w", newline="\n") as f:
        f.write("# The game's files the starting areas need (tools/zones/build_world.py): Cataclysm Classic's\n"
                f"# file id at {common.BUILD}, the path it's put in the game at, and what it is\n")
        for fdid, (path, kind) in sorted(found.items()):
            f.write(f"{fdid}\t{path}\t{kind}\n")
    for table, rows in sorted(b.out.rows.items()):
        print(f"{table}: {len(rows)} rows")
    for table, rows in b.sql.tables.items():
        print(f"world {table}: {len(rows)} rows")
    print(f"files: {len(found)}; not in the build: {len(missing)}")
    for kind, ids in sorted(b.dropped.items()):
        print(f"left for later: {kind}: {len(ids)}")


if __name__ == "__main__":
    main()
