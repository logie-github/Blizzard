"""Cataclysm's spells of the starting areas in 3.3.5a's Spell table (and the world server's spell_dbc):
from Cataclysm Classic's split tables (SpellName, Spell, SpellMisc, SpellEffect and the rest) into
3.3.5a's one row of 234 fields.

A spell 3.3.5a has (the same id, the same name) is 3.3.5a's own. A new one keeps Cataclysm's id where
3.3.5a and the realm's modules haven't it, else gets a new one; the spells, creatures, objects, items
and quests its effects name come with it. Effects and auras whose numbers mean something else in
3.3.5a (Cataclysm's 45 plays a movie; 3.3.5a's adds honor) or nothing (Cataclysm's phase updates,
its altered forms) are made dummies the module's code answers (EFFECT_HOOKS and AURA_HOOKS: each such
spell's script in the world's spell_script_names, src/WorgenGoblinZones.cpp).
"""
import os

import common
import db
from build_tables import game_path
from scripts import SPELL_EDITS, SPELL_POSITIONS

# Cataclysm's effects 3.3.5a has under another number or not at all: as a dummy (3) the module answers.
EFFECT_HOOKS = {45: "movie", 167: "phases", 170: "phases", 252: "teleport"}
# A hook's kind, in its dummy's second misc value (src/WorgenGoblinZones.cpp, ZoneHook).
HOOK_KINDS = {"movie": 1, "phases": 2, "teleport": 3, "altered_form": 4, "worgen_form": 5}
# The hooks the module's code answers (src/WorgenGoblinZones.cpp; Worgen's forms aren't yet: they're
# Worgen here from the start).
SCRIPTED_HOOKS = {"movie", "phases", "teleport"}
# Cataclysm's auras 3.3.5a hasn't: as a dummy aura (4) the module answers.
AURA_HOOKS = {352: "altered_form", 358: "worgen_form"}
# The effects whose misc value names something, by what.
EFFECT_MISC = {
    16: "quest", 28: "creature", 41: "creature", 56: "creature", 76: "object", 86: "object", 90: "creature",
    134: "creature", 50: "object", 104: "object", 105: "object", 106: "object", 107: "object", 112: "creature",
    131: "sound", 132: "sound", 150: "quest", 61: "event",
}
# The auras whose misc value names something.
AURA_MISC = {56: "creature", 296: "vehicle", 261: "phase"}
EFFECT_TRIGGERS = {32, 42, 64, 140, 142, 148, 151, 155, 164}   # (effects whose trigger spell is a spell to bring)
SPELL_DUMMY, AURA_DUMMY = 3, 4


class SpellsMixin:
    """For WorldBuilder: self.table/by_id (Cataclysm Classic's tables), self.ids, self.out, self.done."""

    def spell_rows(self, name, key="SpellID"):
        index_key = ("spell_index", name)
        if index_key not in self.t:
            index = {}
            for r in self.table(name):
                index.setdefault(int(r[key]), []).append(r)
            self.t[index_key] = index
        return self.t[index_key]

    def one(self, name, spell_id):
        rows = [r for r in self.spell_rows(name).get(spell_id, []) if int(r.get("DifficultyID", 0) or 0) == 0]
        return rows[0] if rows else {}

    def stock_spell_names(self):
        if "stock_spell_names" not in self.t:
            layout = [c for c, _ in common.layout(self.dbd, "Spell")]
            i = layout.index("Name_lang")
            self.t["stock_spell_names"] = {r[0]: r[i] for r in self.ids.stock_rows("Spell").values()}
        return self.t["stock_spell_names"]

    def spell(self, cata_id):
        """A spell of Cataclysm's as one of the realm's: 3.3.5a's own when it has it (by id and name),
        else a new row (and what its effects name)."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        names = self.by_id("SpellName")
        name = names.get(cata_id, {}).get("Name_lang")
        if name is None:
            self.drop("spell (not in Cataclysm's tables)", cata_id)
            self.spell_ids[cata_id] = 0
            return 0
        if self.stock_spell_names().get(cata_id) == name:
            self.spell_ids[cata_id] = cata_id
            return cata_id
        key = ("Spell", cata_id)
        if key in self.done:
            return self.done[key]
        self.server_spell_ids()
        our = self.ids.new("Spell", cata_id)
        self.done[key] = self.spell_ids[cata_id] = our
        values = self.spell_values(cata_id, name)
        values["ID"] = our
        self.out.add("Spell", values)
        for what in sorted({h[2] for h in self.spell_hooks if h[0] == cata_id} & SCRIPTED_HOOKS):
            self.sql.add("spell_script_names", {"spell_id": our, "ScriptName": f"spell_worgen_goblin_zones_{what}"})
        for r in self.cpp_spell_scripts().get(cata_id, []) or [{"ScriptName": ""}]:
            name = self.script_name(r["ScriptName"], "spell", cata_id)
            if name:
                self.sql.add("spell_script_names", {"spell_id": our, "ScriptName": name})
        positions = self.target_positions().get(cata_id, [])
        if not positions and cata_id in SPELL_POSITIONS:
            m, x, y, z, o = SPELL_POSITIONS[cata_id]
            positions = [{"EffectIndex": 0, "MapID": m, "PositionX": x, "PositionY": y, "PositionZ": z, "Orientation": o}]
        for r in positions:
            self.sql.add("spell_target_position", {"ID": our, "EffectIndex": r["EffectIndex"], "MapID": r["MapID"],
                                                   "PositionX": float(r["PositionX"]), "PositionY": float(r["PositionY"]),
                                                   "PositionZ": float(r["PositionZ"]), "Orientation": float(r["Orientation"]),
                                                   "VerifiedBuild": -15595})
        return our

    def cpp_spell_scripts(self):
        if "cpp_spell_scripts" not in self.t:
            index = {}
            for r in db.rows(db.CPP_DB, "SELECT * FROM spell_script_names WHERE spell_id > 0"):
                index.setdefault(int(r["spell_id"]), []).append(r)
            self.t["cpp_spell_scripts"] = index
        return self.t["cpp_spell_scripts"]

    # The world's tables that name spells by id (AzerothCore's own rows for spells its game's table
    # hasn't among them: a Cataclysm id one of them names isn't free).
    SERVER_SPELL_TABLES = {
        "spell_area": "spell", "spell_bonus_data": "entry", "spell_cooldown_overrides": "Id",
        "spell_custom_attr": "spell_id", "spell_enchant_proc_data": "entry", "spell_group": "spell_id",
        "spell_linked_spell": "spell_trigger", "spell_loot_template": "Entry", "spell_pet_auras": "spell",
        "spell_proc": "SpellId", "spell_ranks": "spell_id", "spell_required": "spell_id", "spell_scripts": "id",
        "spell_script_names": "spell_id", "spell_target_position": "ID", "spell_threat": "entry",
        "spell_dbc": "ID",
    }

    def server_spell_ids(self):
        if "server_spell_ids" not in self.t:
            taken = self.ids.taken_ids("Spell")
            for table, column in self.SERVER_SPELL_TABLES.items():
                if column in db.column_names(db.AC_DB, table):
                    taken |= {abs(int(r[column])) for r in db.rows(db.AC_DB, f"SELECT DISTINCT `{column}` FROM `{table}`")}
            self.t["server_spell_ids"] = True

    def target_positions(self):
        """CPP's spell_target_position, by spell (a teleport's place: on Gilneas's map 654, which the
        module makes the player's own map of Gilneas)."""
        if "target_positions" not in self.t:
            index = {}
            for r in db.rows(db.CPP_DB, "SELECT * FROM spell_target_position"):
                index.setdefault(int(r["ID"]), []).append(r)
            self.t["target_positions"] = index
        return self.t["target_positions"]

    def spell_values(self, cata_id, name):
        s = self.by_id("Spell").get(cata_id, {})
        misc = self.one("SpellMisc", cata_id)
        v = {"Name_lang": name, "NameSubtext_lang": s.get("NameSubtext_lang", ""), "Description_lang": s.get("Description_lang", ""),
             "AuraDescription_lang": s.get("AuraDescription_lang", "")}
        attrs = ["Attributes", "AttributesEx", "AttributesExB", "AttributesExC", "AttributesExD", "AttributesExE",
                 "AttributesExF", "AttributesExG"]
        for i, a in enumerate(attrs):
            v[a] = int(misc.get(f"Attributes_{i}", 0) or 0) & 0xFFFFFFFF
        v["CastingTimeIndex"] = self.spell_index("SpellCastTimes", misc.get("CastingTimeIndex"))
        v["DurationIndex"] = self.spell_index("SpellDuration", misc.get("DurationIndex"))
        v["RangeIndex"] = self.spell_index("SpellRange", misc.get("RangeIndex"))
        v["SchoolMask"] = int(misc.get("SchoolMask", 1) or 1)
        v["Speed"] = float(misc.get("Speed", 0) or 0)
        v["SpellIconID"] = self.spell_icon(misc.get("SpellIconFileDataID"))
        v["ActiveIconID"] = self.spell_icon(misc.get("ActiveIconFileDataID"))
        cat = self.one("SpellCategories", cata_id)
        v.update({"Category": self.spell_category(cat.get("Category")), "DispelType": int(cat.get("DispelType", 0) or 0),
                  "Mechanic": int(cat.get("Mechanic", 0) or 0), "DefenseType": int(cat.get("DefenseType", 0) or 0),
                  "PreventionType": int(cat.get("PreventionType", 0) or 0),
                  "StartRecoveryCategory": int(cat.get("StartRecoveryCategory", 0) or 0)})
        cd = self.one("SpellCooldowns", cata_id)
        v.update({"RecoveryTime": int(cd.get("RecoveryTime", 0) or 0), "CategoryRecoveryTime": int(cd.get("CategoryRecoveryTime", 0) or 0),
                  "StartRecoveryTime": int(cd.get("StartRecoveryTime", 0) or 0)})
        it = self.one("SpellInterrupts", cata_id)
        v.update({"InterruptFlags": int(it.get("InterruptFlags", 0) or 0) & 0x1F,
                  "AuraInterruptFlags": int(it.get("AuraInterruptFlags_0", 0) or 0) & 0x3FFFFFFF,
                  "ChannelInterruptFlags": int(it.get("ChannelInterruptFlags_0", 0) or 0) & 0x3FFFFFFF})
        ao = self.one("SpellAuraOptions", cata_id)
        v.update({"CumulativeAura": int(ao.get("CumulativeAura", 0) or 0), "ProcChance": int(ao.get("ProcChance", 0) or 0),
                  "ProcCharges": int(ao.get("ProcCharges", 0) or 0), "ProcTypeMask": int(ao.get("ProcTypeMask_0", 0) or 0)})
        ar = self.one("SpellAuraRestrictions", cata_id)
        for c in ("CasterAuraState", "TargetAuraState", "ExcludeCasterAuraState", "ExcludeTargetAuraState"):
            v[c] = int(ar.get(c, 0) or 0)
        for c in ("CasterAuraSpell", "TargetAuraSpell", "ExcludeCasterAuraSpell", "ExcludeTargetAuraSpell"):
            v[c] = self.spell(ar.get(c)) if int(ar.get(c, 0) or 0) else 0
        cr = self.one("SpellCastingRequirements", cata_id)
        v.update({"FacingCasterFlags": int(cr.get("FacingCasterFlags", 0) or 0), "RequiresSpellFocus": int(cr.get("RequiresSpellFocus", 0) or 0),
                  "MinFactionID": self.faction(cr.get("MinFactionID")), "MinReputation": int(cr.get("MinReputation", 0) or 0),
                  "RequiredAuraVision": int(cr.get("RequiredAuraVision", 0) or 0), "RequiredAreasID": 0})
        if int(cr.get("RequiredAreasID", 0) or 0):
            self.drop("spell area group", cata_id)
        lv = self.one("SpellLevels", cata_id)
        v.update({"BaseLevel": int(lv.get("BaseLevel", 0) or 0), "MaxLevel": int(lv.get("MaxLevel", 0) or 0),
                  "SpellLevel": int(lv.get("SpellLevel", 0) or 0)})
        pw = self.one("SpellPower", cata_id)
        v.update({"PowerType": int(pw.get("PowerType", 0) or 0) & 0xFF if int(pw.get("PowerType", 0) or 0) >= 0 else 0,
                  "ManaCost": int(pw.get("ManaCost", 0) or 0), "ManaCostPerLevel": int(pw.get("ManaCostPerLevel", 0) or 0),
                  "ManaPerSecond": int(pw.get("ManaPerSecond", 0) or 0), "ManaCostPct": int(float(pw.get("PowerCostPct", 0) or 0))})
        if v["PowerType"] > 6:
            v["PowerType"], v["ManaCost"] = 0, 0       # (Cataclysm's powers past runic power: none here)
        rg = self.one("SpellReagents", cata_id)
        for i in range(8):
            if int(rg.get(f"Reagent_{i}", 0) or 0) > 0:
                v[f"Reagent_{i}"] = self.item(rg[f"Reagent_{i}"])
                v[f"ReagentCount_{i}"] = int(rg.get(f"ReagentCount_{i}", 0) or 0)
        sh = self.one("SpellShapeshift", cata_id)
        v.update({"ShapeshiftMask_0": int(sh.get("ShapeshiftMask_0", 0) or 0), "ShapeshiftMask_1": int(sh.get("ShapeshiftMask_1", 0) or 0),
                  "ShapeshiftExclude_0": int(sh.get("ShapeshiftExclude_0", 0) or 0), "ShapeshiftExclude_1": int(sh.get("ShapeshiftExclude_1", 0) or 0),
                  "StanceBarOrder": int(sh.get("StanceBarOrder", 0) or 0)})
        tr = self.one("SpellTargetRestrictions", cata_id)
        v.update({"Targets": int(tr.get("Targets", 0) or 0), "TargetCreatureType": int(tr.get("TargetCreatureType", 0) or 0),
                  "MaxTargets": int(tr.get("MaxTargets", 0) or 0), "MaxTargetLevel": int(tr.get("MaxTargetLevel", 0) or 0)})
        eq = self.one("SpellEquippedItems", cata_id)
        v.update({"EquippedItemClass": int(eq.get("EquippedItemClass", -1) or -1), "EquippedItemSubclass": int(eq.get("EquippedItemSubclass", 0) or 0),
                  "EquippedItemInvTypes": int(eq.get("EquippedItemInvTypes", 0) or 0)})
        co = self.one("SpellClassOptions", cata_id)
        v["SpellClassSet"] = int(co.get("SpellClassSet", 0) or 0)
        for i in range(3):
            v[f"SpellClassMask_{i}"] = int(co.get(f"SpellClassMask_{i}", 0) or 0) & 0xFFFFFFFF
        v["SpellVisualID_0"] = self.spell_visual(cata_id)
        # Its effects (3.3.5a has three).
        effects = sorted((e for e in self.spell_rows("SpellEffect").get(cata_id, []) if int(e.get("DifficultyID", 0) or 0) == 0),
                         key=lambda e: int(e["EffectIndex"]))
        if len([e for e in effects if int(e["EffectIndex"]) > 2]):
            self.drop("spell with more than three effects", cata_id)
        for e in effects:
            i = int(e["EffectIndex"])
            if i > 2:
                continue
            self.effect_values(cata_id, i, e, v)
        return v

    def effect_values(self, cata_id, i, e, v):
        effect, aura = int(e["Effect"]), int(e["EffectAura"])
        misc, misc_b = int(e["EffectMiscValue_0"]), int(e["EffectMiscValue_1"])
        if effect in EFFECT_HOOKS:
            # (the dummy keeps the value the module reads, a movie's narration here, and its kind)
            misc = self.movie_sound(misc) if EFFECT_HOOKS[effect] == "movie" else misc
            self.hook(cata_id, i, EFFECT_HOOKS[effect], misc)
            effect, misc_b = SPELL_DUMMY, HOOK_KINDS[EFFECT_HOOKS[effect]]
        elif effect > 164:
            self.drop(f"spell effect {effect}", cata_id)
            effect = SPELL_DUMMY
        if aura in AURA_HOOKS:
            self.hook(cata_id, i, AURA_HOOKS[aura], misc)
            aura, misc, misc_b = AURA_DUMMY, 0, HOOK_KINDS[AURA_HOOKS[aura]]
        elif aura > 316:
            self.drop(f"spell aura {aura}", cata_id)
            aura = AURA_DUMMY
        kind = EFFECT_MISC.get(effect) or (AURA_MISC.get(aura) if effect in (6, 35, 119, 128, 129, 143, 174) else None)
        if kind == "phase":
            # (Cataclysm's phase id is its second value; its first, a phase mask of its own)
            misc, misc_b = self.misc(kind, misc_b, cata_id), 0
        elif kind:
            misc = self.misc(kind, misc, cata_id)
        if effect == 28 or effect == 41:                  # (a summon: its properties too)
            misc_b = self.summon_properties(misc_b)
        trigger = int(e["EffectTriggerSpell"] or 0)
        v.update({f"Effect_{i}": effect, f"EffectAura_{i}": aura,
                  f"EffectBasePoints_{i}": int(float(e["EffectBasePoints"] or 0)), f"EffectDieSides_{i}": int(e["EffectDieSides"] or 0),
                  f"EffectRealPointsPerLevel_{i}": float(e["EffectRealPointsPerLevel"] or 0),
                  f"EffectMechanic_{i}": int(e["EffectMechanic"] or 0), f"ImplicitTargetA_{i}": self.target(int(e["ImplicitTarget_0"]), cata_id),
                  f"ImplicitTargetB_{i}": self.target(int(e["ImplicitTarget_1"]), cata_id),
                  f"EffectRadiusIndex_{i}": self.spell_index("SpellRadius", e["EffectRadiusIndex_0"]),
                  f"EffectAuraPeriod_{i}": int(e["EffectAuraPeriod"] or 0), f"EffectAmplitude_{i}": float(e["EffectAmplitude"] or 0),
                  f"EffectChainTargets_{i}": int(e["EffectChainTargets"] or 0),
                  f"EffectItemType_{i}": self.item(e["EffectItemType"]) if int(e["EffectItemType"] or 0) else 0,
                  f"EffectMiscValue_{i}": misc, f"EffectMiscValueB_{i}": misc_b,
                  f"EffectTriggerSpell_{i}": self.spell(trigger) if trigger else 0,
                  f"EffectPointsPerCombo_{i}": float(e["EffectPointsPerResource"] or 0),
                  f"EffectChainAmplitude_{i}": float(e["EffectChainAmplitude"] or 0),
                  f"EffectBonusCoefficient_{i}": float(e["EffectBonusCoefficient"] or 0)})
        for k, letter in enumerate("ABC"):
            v[f"EffectSpellClassMask{letter}_{i}"] = int(e[f"EffectSpellClassMask_{k}"] or 0) & 0xFFFFFFFF
        # A vehicle's summon: its value is the spell the summoner gets in with (AzerothCore's as Cataclysm's).
        properties = self.by_id("SummonProperties").get(int(e["EffectMiscValue_1"] or 0), {})
        ride = int(float(e["EffectBasePoints"] or 0))
        if effect == 28 and int(properties.get("Control", 0) or 0) == 4 and ride > 8:
            v[f"EffectBasePoints_{i}"] = self.spell(ride)
        for column, value in SPELL_EDITS.get(cata_id, {}).get(i, {}).items():
            v[f"{column}_{i}"] = value

    def target(self, target, cata_id):
        if target <= 104:
            return target
        self.drop(f"spell target {target}", cata_id)
        return {105: 1, 106: 6, 107: 18, 108: 15, 109: 15, 110: 15}.get(target, 1)

    def misc(self, kind, value, cata_id):
        if not value:
            return value
        if kind == "creature":
            self.need_creature(value)
            return self.creature_entry(value)
        if kind == "object":
            self.need_object(value)
            return self.object_entry(value)
        if kind == "quest":
            return self.quest_id(value)
        if kind == "sound":
            return self.sound(value)
        if kind == "vehicle":
            return self.vehicle(value)
        if kind == "phase":
            return self.phase_mask(value, 0)
        self.drop(f"spell {kind}", cata_id)
        return 0

    def movie_sound(self, movie_id):
        """A movie of Cataclysm's as its narration: Cataclysm Classic's game has the movies' sound and
        not their pictures (the Worgen's and the Goblins'). A SoundEntries row of it; 0 for none."""
        key = ("movie", movie_id)
        if key in self.done:
            return self.done[key]
        movie = self.by_id("Movie").get(movie_id)
        our = 0
        if movie is not None and int(movie["AudioFileDataID"]) in self.names:
            path = self.file(movie["AudioFileDataID"], "sound")
            our = self.ids.new("SoundEntries")
            self.out.add("SoundEntries", {
                "ID": our, "SoundType": 28, "Name": f"CataclysmMovie{movie_id}", "File_0": os.path.basename(path), "Freq_0": 1,
                "DirectoryBase": game_path(os.path.dirname(path)), "VolumeFloat": int(movie["Volume"]) / 100,
                "Flags": 0, "MinDistance": 8.0, "DistanceCutoff": 45.0, "EAXDef": 0})
        else:
            self.drop("movie", movie_id)
        self.done[key] = our
        return our

    def hook(self, cata_id, index, what, value):
        self.spell_hooks.append((cata_id, index, what, value))

    def spell_index(self, table, cata_id):
        """A cast time, duration, range or radius (3.3.5a's of that id when it's the same, else new)."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = (table, cata_id)
        if key in self.done:
            return self.done[key]
        r = self.by_id(table).get(cata_id)
        if r is None:
            return 0
        values = {}
        for col, kind in common.layout(self.dbd, table):
            if col == "ID" or "#" in col:
                continue
            src = r.get(col, "0")
            values[col] = (float(src or 0) if kind == "f" else (src or "") if kind == "s" else int(float(src or 0)))
        stock = self.ids.stock_rows(table).get(cata_id)
        if stock is not None and all(abs(a - b) < 1e-3 if isinstance(a, float) else a == b
                                     for a, b, (c, k) in zip(stock[1:], [values.get(c, 0) for c, _ in common.layout(self.dbd, table)[1:]],
                                                             common.layout(self.dbd, table)[1:]) if k != "s"):
            self.done[key] = cata_id
            return cata_id
        values["ID"] = self.ids.new(table, cata_id)
        self.out.add(table, values)
        self.done[key] = values["ID"]
        return values["ID"]

    def spell_icon(self, fdid):
        fdid = int(fdid or 0)
        if not fdid or fdid not in self.names:
            return 0
        key = ("SpellIcon", fdid)
        if key in self.done:
            return self.done[key]
        path = game_path(self.names[fdid])
        stem = path.rsplit(".", 1)[0]
        if "stock_icons" not in self.t:
            self.t["stock_icons"] = {r[1].lower(): r[0] for r in self.ids.stock_rows("SpellIcon").values()}
        found = self.t["stock_icons"].get(stem.lower())
        if found is None:
            found = self.ids.new("SpellIcon")
            self.out.add("SpellIcon", {"ID": found, "TextureFilename": stem})
            self.add_file(fdid, "ui")
        self.done[key] = found
        return found

    def spell_category(self, cata_id):
        cata_id = int(cata_id or 0)
        if cata_id <= 0 or cata_id in self.ids.stock_rows("SpellCategory"):
            return cata_id
        return 0

    def spell_visual(self, cata_id):
        """Its look (SpellXSpellVisual's first): 3.3.5a's of that id when it has it; Cataclysm's new
        looks are for later (their kits, effects and models)."""
        rows = sorted(self.spell_rows("SpellXSpellVisual").get(cata_id, []), key=lambda r: int(r.get("Priority", 0) or 0))
        for r in rows:
            visual = int(r["SpellVisualID"])
            if visual in self.ids.stock_rows("SpellVisual"):
                return visual
            self.drop("spell visual", visual)
        return 0

    def summon_properties(self, cata_id):
        cata_id = int(cata_id or 0)
        if cata_id <= 0 or cata_id in self.ids.stock_rows("SummonProperties"):
            return cata_id
        key = ("SummonProperties", cata_id)
        if key not in self.done:
            r = self.by_id("SummonProperties").get(cata_id)
            if r is None:
                self.done[key] = 0
            else:
                values = {"ID": self.ids.new("SummonProperties", cata_id), "Control": int(r["Control"]),
                          "Faction": self.faction_template(r["Faction"]) if int(r["Faction"]) else 0,
                          "Title": int(r["Title"]), "Slot": int(r["Slot"]), "Flags": int(r["Flags_0"] if "Flags_0" in r else r.get("Flags", 0))}
                self.out.add("SummonProperties", values)
                self.done[key] = values["ID"]
        return self.done[key]
