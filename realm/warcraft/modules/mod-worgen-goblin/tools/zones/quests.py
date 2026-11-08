"""The starting areas' quests, SmartAI, loot, wares, trainers, graveyards and area triggers: the
Cataclysm Preservation Project's, in AzerothCore's tables, every row new (quest ids from ENTRY like
the creatures'), the quests the Worgen's (Gilneas) or the Goblins' (Kezan, the Lost Isles) alone.
"""
import common
import db

# The zones' quests by their sort (zone): whose they are (3.3.5a's race bits: the Worgen 12, the Goblins 9).
WORGEN, GOBLIN = 1 << 11, 1 << 8
QUEST_ZONES = {4714: WORGEN, 4755: WORGEN, 4737: GOBLIN, 4720: GOBLIN}
# The class quests' spells a 3.3.5a character hasn't at the start (Cataclysm's trainers taught them at
# level 1; 3.3.5a's teach them later, or never: Primal Strike): the class's own starting spell in
# their place, in the quest's texts too. Cataclysm's spell: (3.3.5a's, its name, the stand-in's).
STAND_INS = {100: (78, "Charge", "Heroic Strike"), 56641: (75, "Steady Shot", "Auto Shot"),
             2061: (2050, "Flash Heal", "Lesser Heal"), 5143: (133, "Arcane Missiles", "Fireball"),
             774: (5185, "Rejuvenation", "Healing Touch"), 348: (686, "Immolate", "Shadow Bolt"),
             73899: (403, "Primal Strike", "Lightning Bolt")}
# The Lost Isles' phases, which CPP hasn't (its creatures there are in phases 170 to 185, which nothing
# gave a player): the goblins' camp moving on with the story, each phase Cataclysm's own aura ("Quest
# Phase 01" to "10") over the zone from the quest that leads into it taken (its ender stands there) until
# another is rewarded. The quests that bound them are the story's own (where each phase's quest givers
# and enders stand): (the phase's spell, the quest from whose taking it's there or 0, the quest after
# whose reward it's gone or 0).
LOST_ISLES = 4720
LOST_ISLES_PHASES = [
    (67851, 0, 14242),        # 170: Shipwreck Shore, the Kaja'mite Cavern, the Vicious Vale (to Precious Cargo)
    (67852, 14237, 14242),    # 171: the Savage Glen's scouts (Forward Movement to Precious Cargo)
    (67853, 14241, 14326),    # 172: the Vengeance Wake, the Alliance Beachhead (Get to the Gyrochoppa! to Meet Me Up Top)
    (67854, 14326, 14245),    # 179: Thrall's camp, the ship's sailors (Meet Me Up Top to It's a Town-In-A-Box)
    (68750, 14245, 0),        # 180: Town-In-A-Box, Vashj'elan, Raptor Rise (from It's a Town-In-A-Box)
    (72157, 24897, 24940),    # 181: the town under attack, Oomlot Village (Get Back to Town to Up the Volcano)
    (72676, 24937, 24958),    # 182: the volcano (Oomlot Dealt With to Volcanoth!)
    (73065, 24958, 25213),    # 183: the Gallywix Labor Mine (Volcanoth! to The Slave Pits)
    (73756, 25125, 0),        # 184: the Slave Pits, the oil platform, the docks (from Light at the End of the Tunnel)
    (74025, 25213, 0),        # 185: the final confrontation (from The Slave Pits)
]
# Gilneas's third chapter likewise (CPP's phase auras there end at The King's Observatory, 14466):
# Cataclysm's "Phase - Quest Zone-Specific 09" to "16", after CPP's 05 to 08 (phases 180 to 183)
# there, from a quest taken (or rewarded: TAKEN) until another is rewarded, over Gilneas and Gilneas City.
GILNEAS_ZONES = (4714, 4755)
GILNEAS_PHASES = [
    (68483, 14466, 24438),    # 183, on until Exodus (CPP's ends at 14466, before King Genn gives Exodus there)
    (69077, 14465, 14466),    # 184: Greymane Manor (To Greymane Manor to The King's Observatory)
    (69484, 24438, 24904),    # 186: Stormglen, Tal'doren, the Blackwald (Exodus to The Battle for Gilneas City)
    (69485, 24904, 24903),    # 187: the battle in the city (to Vengeance or Survival)
    (70696, 24903, 24678),    # 190: the cathedral after it (Vengeance or Survival to Knee-Deep)
    (69486, 24678, 24680),    # 188: the Northern Headlands (Knee-Deep to Keel Harbor)
    (70695, 24680, 14434),    # 189: the Headlands, Keel Harbor (Keel Harbor to Rut'theran Village)
    (74093, 24680, 14434),    # 191: Keel Harbor's ships, the same
]
# The way out into Wrath's world (stage 5): Warchief's Emissary, which Cataclysm's Kor'kron Loyalist
# takes in its Orgrimmar, taken by 3.3.5a's Thrall in Grommash Hold (the module's code takes the Goblins
# there on taking it; the Worgen to Rut'theran Village after Rut'theran Village: WorgenGoblinZones.cpp).
WAY_OUT = {25266: 4949}
REWARDED, NOT_REWARDED = 1 << 6, (1 << 0) | (1 << 1) | (1 << 3)    # (AzerothCore's quest status bits)
TAKEN = (1 << 1) | (1 << 3) | (1 << 6)
# What the quests say of a Cataclysm spell that is untrue of its stand-in (Arcane Missiles' proc), left out.
STAND_IN_CUTS = ("$B$BRemember, Arcane Missiles have a chance to activate through the use of other offensive spells. "
                 "Use your Fireball spell first on the Training Dummy to enable the casting of your Arcane Missiles spell.",)
# SmartAI: what each parameter names, by event, action and target type (the same numbers in both
# cores for every type these zones use; CPP's 114, move by an offset, is AzerothCore's 46, forward).
EVENT_PARAMS = {8: {1: "spell"}, 19: {1: "quest"}, 20: {1: "quest"}, 40: {2: "path"}, 52: {2: "creature"},
                62: {1: "gossip"}, 73: {1: "creature"}, 22: {1: "spell"}, 23: {1: "spell"}, 24: {1: "spell"}}
ACTION_PARAMS = {2: {1: "faction"}, 3: {1: "creature", 2: "display"}, 11: {1: "spell"}, 12: {1: "creature"}, 15: {1: "quest"},
                 26: {1: "quest"}, 28: {1: "spell"}, 33: {1: "creature"}, 36: {1: "creature"}, 43: {1: "creature", 2: "display"},
                 50: {1: "object"}, 53: {2: "path", 4: "quest"}, 56: {1: "item"}, 57: {1: "item"}, 75: {1: "spell"},
                 80: {1: "actionlist"}, 85: {1: "spell"}, 86: {1: "spell"},
                 87: {1: "actionlist", 2: "actionlist", 3: "actionlist", 4: "actionlist", 5: "actionlist", 6: "actionlist"}}
TARGET_PARAMS = {9: {1: "creature"}, 10: {1: "guid", 2: "creature"}, 11: {1: "creature"}, 13: {1: "object"},
                 14: {1: "object guid", 2: "object"}, 15: {1: "object"}, 19: {1: "creature"}, 20: {1: "object"}}
# Conditions' values that name something, by condition type: (value index, kind).
CONDITION_VALUES = {1: [(1, "spell")], 2: [(1, "item")], 5: [(1, "faction")], 8: [(1, "quest")], 9: [(1, "quest")],
                    14: [(1, "quest")], 28: [(1, "quest")], 43: [(1, "quest")], 47: [(1, "quest")], 29: [(1, "creature")],
                    30: [(1, "object")], 31: [(2, "creature")]}


def stand_in_text(text, old, new):
    """A class quest's text with its spell's stand-in (STAND_INS) named in its place."""
    for cut in STAND_IN_CUTS:
        text = text.replace(cut, "")
    return text.replace(old, new)


class QuestsMixin:
    def quest_id(self, cata_id):
        """A quest of the starting areas as the realm's (0 for one of elsewhere a row names: Icecrown's,
        Azshara's, the way into Orgrimmar's, which stage 5 brings in as Wrath's own NPCs give it)."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        if cata_id not in self.local_quests():
            self.drop("quest outside the starting areas", cata_id)
            return 0
        if cata_id not in self.quests_seen:
            self.quests_seen.add(cata_id)
            self.quest_queue.append(cata_id)
        return self.ENTRY + cata_id

    def local_quests(self):
        """The starting areas' quests: their zones' (QuestSortID), and the ones a creature or object
        that stands on their maps gives."""
        if "local_quests" not in self.t:
            sorts = ", ".join(str(z) for z in QUEST_ZONES)
            ids = {int(r["ID"]) for r in db.rows(db.CPP_DB, f"SELECT ID FROM quest_template WHERE QuestSortID IN ({sorts})")}
            ids |= {int(r["quest"]) for r in db.rows(db.CPP_DB, f"SELECT quest FROM creature_queststarter WHERE id IN ({db.ids_in(self.creatures)})")}
            ids |= {int(r["quest"]) for r in db.rows(db.CPP_DB, f"SELECT quest FROM gameobject_queststarter WHERE id IN ({db.ids_in(self.objects)})")}
            self.t["local_quests"] = ids
        return self.t["local_quests"]

    def races_of(self, sort, cpp_mask):
        mine = QUEST_ZONES.get(sort)
        if mine:
            return mine
        from build_world import race_mask
        mask = race_mask(cpp_mask & 0xFFFFFFFF) if cpp_mask else 0
        return (mask & (WORGEN | GOBLIN)) or (WORGEN | GOBLIN)

    def quests(self):
        for q in sorted(self.local_quests()):
            self.quest_id(q)
        while self.quest_queue:
            batch, self.quest_queue = self.quest_queue, []
            templates = {int(r["ID"]): r for r in db.rows(db.CPP_DB, f"SELECT * FROM quest_template WHERE ID IN ({db.ids_in(batch)})")}
            addons = {int(r["ID"]): r for r in db.rows(db.CPP_DB, f"SELECT * FROM quest_template_addon WHERE ID IN ({db.ids_in(batch)})")}
            for qid in batch:
                t = templates.get(qid)
                if t is None:
                    self.drop("quest (not in CPP)", qid)
                    continue
                self.quest_row(qid, t, addons.get(qid, {}))
            self.quest_texts(batch)

    def quest_row(self, qid, t, a):
        v = {}
        same = ["QuestType", "QuestLevel", "MinLevel", "QuestSortID", "QuestInfoID", "SuggestedGroupNum", "RequiredFactionValue1",
                "RequiredFactionValue2", "RewardXPDifficulty", "RewardMoney", "RewardHonor", "RewardKillHonor", "Flags",
                "RequiredPlayerKills", "POIContinent", "POIx", "POIy", "POIPriority", "RewardTalents", "RewardArenaPoints",
                "LogTitle", "LogDescription", "QuestDescription", "AreaDescription", "QuestCompletionLog",
                "ObjectiveText1", "ObjectiveText2", "ObjectiveText3", "ObjectiveText4"]
        for c in same:
            v[c] = t[c]
        stand_in = STAND_INS.get(int(t["RequiredSpell"] or 0))
        if stand_in:
            self.renamed[qid] = stand_in[1:]
            for c in same:
                if isinstance(v[c], str):
                    v[c] = stand_in_text(v[c], *stand_in[1:])
        v["ID"] = self.ENTRY + qid
        v["Flags"] = int(t["Flags"]) & 0x000FFFFF
        v["RewardMoneyDifficulty"] = 0
        v["RequiredFactionId1"] = self.faction(t["RequiredFactionId1"])
        v["RequiredFactionId2"] = self.faction(t["RequiredFactionId2"])
        v["RewardNextQuest"] = self.quest_id(t["RewardNextQuest"])
        v["RewardDisplaySpell"] = self.spell(t["RewardDisplaySpell"])
        v["RewardSpell"] = self.spell(t["RewardSpell"])
        v["StartItem"] = self.item(t["StartItem"])
        for i in range(1, 5):
            v[f"RewardItem{i}"], v[f"RewardAmount{i}"] = self.item(t[f"RewardItem{i}"]), t[f"RewardAmount{i}"]
            v[f"ItemDrop{i}"], v[f"ItemDropQuantity{i}"] = self.item(t[f"ItemDrop{i}"]), t[f"ItemDropQuantity{i}"]
            npc = int(t[f"RequiredNpcOrGo{i}"])
            v[f"RequiredNpcOrGo{i}"] = (self.creature_entry(npc) if npc > 0 else -self.object_entry(-npc) if npc < 0 else 0)
            if npc > 0:
                self.need_creature(npc)
            elif npc < 0:
                self.need_object(-npc)
            v[f"RequiredNpcOrGoCount{i}"] = t[f"RequiredNpcOrGoCount{i}"]
        for i in range(1, 7):
            v[f"RewardChoiceItemID{i}"], v[f"RewardChoiceItemQuantity{i}"] = self.item(t[f"RewardChoiceItemID{i}"]), t[f"RewardChoiceItemQuantity{i}"]
            v[f"RequiredItemId{i}"], v[f"RequiredItemCount{i}"] = self.item(t[f"RequiredItemId{i}"]), t[f"RequiredItemCount{i}"]
        for i in range(1, 6):
            v[f"RewardFactionID{i}"] = self.faction(t[f"RewardFactionID{i}"])
            v[f"RewardFactionValue{i}"] = t[f"RewardFactionValue{i}"]
            v[f"RewardFactionOverride{i}"] = t[f"RewardFactionOverride{i}"]
        v["RewardTitle"] = 0
        v["TimeAllowed"] = int(a.get("TimeAllowed", 0) or 0)
        v["AllowableRaces"] = self.races_of(int(t["QuestSortID"]), int(a.get("AllowableRaces", 0) or 0))
        v["Unknown0"] = 0
        v["VerifiedBuild"] = -15595
        if int(t["RequiredSpell"] or 0) and int(t["RequiredNpcOrGo1"] or 0) <= 0:
            self.drop("quest's required spell", qid)     # (with a credit creature: the module's code, cast_credits)
        self.sql.add("quest_template", v)
        if a:
            self.sql.add("quest_template_addon", {
                "ID": self.ENTRY + qid, "MaxLevel": a["MaxLevel"], "AllowableClasses": a["AllowableClasses"],
                "SourceSpellID": self.spell(a["SourceSpellID"]), "PrevQuestID": self.quest_ref(a["PrevQuestID"]),
                "NextQuestID": self.quest_ref(a["NextQuestID"]), "ExclusiveGroup": self.quest_ref(a["ExclusiveGroup"]),
                "BreadcrumbForQuestId": self.quest_ref(a["BreadcrumbForQuestId"]), "RewardMailTemplateID": 0, "RewardMailDelay": 0,
                "RequiredSkillID": a["RequiredSkillID"], "RequiredSkillPoints": a["RequiredSkillPoints"],
                "RequiredMinRepFaction": self.faction(a["RequiredMinRepFaction"]), "RequiredMaxRepFaction": self.faction(a["RequiredMaxRepFaction"]),
                "RequiredMinRepValue": a["RequiredMinRepValue"], "RequiredMaxRepValue": a["RequiredMaxRepValue"],
                "ProvidedItemCount": a["ProvidedItemCount"], "SpecialFlags": a["SpecialFlags"]})
            if int(a.get("RewardMailTemplateID", 0) or 0):
                self.drop("quest reward mail", qid)

    def quest_ref(self, value):
        """A quest named by another (its chain: negative for "this one's group"), kept in the chain's sign."""
        value = int(value or 0)
        if value == 0:
            return 0
        return self.quest_id(abs(value)) * (1 if value > 0 else -1)

    def quest_texts(self, batch):
        ids = db.ids_in(batch)
        for table in ("quest_offer_reward", "quest_request_items", "quest_details"):
            for r in db.rows(db.CPP_DB, f"SELECT * FROM {table} WHERE ID IN ({ids})"):
                r = dict(r)
                old, new = self.renamed.get(int(r["ID"]), (None, None))
                if old:
                    r = {k: stand_in_text(v, old, new) if isinstance(v, str) else v for k, v in r.items()}
                r["ID"] = self.ENTRY + int(r["ID"])
                self.sql.add(table, r)
        for r in db.rows(db.CPP_DB, f"SELECT * FROM quest_poi WHERE QuestID IN ({ids})"):
            area = self.world_map_area(r["MapID"], r["WorldMapAreaID"])
            self.sql.add("quest_poi", {"QuestID": self.ENTRY + int(r["QuestID"]), "id": r["BlobIndex"], "ObjectiveIndex": r["ObjectiveIndex"],
                                       "MapID": self.poi_map(r["MapID"]), "WorldMapAreaId": area, "Floor": r["Floor"],
                                       "Priority": r["Priority"], "Flags": r["Flags"], "VerifiedBuild": -15595})
        for r in db.rows(db.CPP_DB, f"SELECT * FROM quest_poi_points WHERE QuestID IN ({ids})"):
            r = dict(r)
            r["QuestID"] = self.ENTRY + int(r["QuestID"])
            self.sql.add("quest_poi_points", r)

    def poi_map(self, map_id):
        return 638 if int(map_id) == 654 else int(map_id)   # (Gilneas's quests are on its map as it starts)

    def world_map_area(self, map_id, cata_area):
        """Cataclysm's WorldMapArea as ours (by the zone it shows: the starting areas' own rows)."""
        zones = {545: 4714, 611: 4755, 678: 4714, 679: 4714, 544: 4720, 605: 4737}
        zone = zones.get(int(cata_area))
        for row in self.out.rows.get("WorldMapArea", []):
            if row[2] == zone and row[1] == self.poi_map(map_id):
                return row[0]
        return 0

    def quest_relations(self):
        for table, kind, entries in (("creature_queststarter", "creature", self.creatures_done),
                                     ("creature_questender", "creature", self.creatures_done),
                                     ("gameobject_queststarter", "object", self.objects_done),
                                     ("gameobject_questender", "object", self.objects_done)):
            for r in db.rows(db.CPP_DB, f"SELECT * FROM {table} WHERE id IN ({db.ids_in(entries)}) AND quest IN ({db.ids_in(self.quests_seen)})"):
                self.sql.add(table, {"id": self.ENTRY + int(r["id"]), "quest": self.ENTRY + int(r["quest"])})
        # The way out: a quest Cataclysm ends in a city of its own whose ender 3.3.5a's world hasn't, taken
        # by that city's own (nothing new stands there: WAY_OUT).
        for quest, ender in WAY_OUT.items():
            if quest in self.quests_seen:
                self.sql.add("creature_questender", {"id": ender, "quest": self.ENTRY + quest})

    # --- SmartAI -----------------------------------------------------------------------------------

    def smart_param(self, kind, value, owner_maps):
        value = int(value or 0)
        if not value:
            return value
        if kind == "spell":
            return self.spell(value)
        if kind == "quest":
            return self.quest_id(value)
        if kind == "creature":
            self.need_creature(value)
            return self.creature_entry(value)
        if kind == "object":
            self.need_object(value)
            return self.object_entry(value)
        if kind == "item":
            return self.item(value)
        if kind == "faction":
            return self.faction_template(value)
        if kind == "display":
            return self.display(value)
        if kind == "gossip":
            return self.gossip_menu(value)
        if kind == "path":
            self.paths_needed.add(value)
            return self.PATH + value
        if kind == "actionlist":
            self.actionlists_needed.add(value)
            return self.PATH + value
        return value

    def smart_scripts(self, new):
        """The SmartAI of the creatures and objects in [new] (by kind, and a creature's by spawn: on each
        of its spawn's maps), and of the action lists they call."""
        creatures, objects = new & self.creatures_done, new & self.objects_done
        rows = db.rows(db.CPP_DB, f"SELECT * FROM smart_scripts WHERE (source_type = 0 AND entryorguid IN ({db.ids_in(creatures)})) "
                                  f"OR (source_type = 1 AND entryorguid IN ({db.ids_in(objects)}))")
        spawns = {int(r["guid"]): r for r in self.cpp_spawns if int(r["id"]) in creatures}
        guid_rows = db.rows(db.CPP_DB, f"SELECT * FROM smart_scripts WHERE source_type = 0 AND entryorguid < 0 AND -entryorguid IN ({db.ids_in(spawns)})")
        for r in rows:
            self.smart_row(r, self.ENTRY + int(r["entryorguid"]))
        for r in guid_rows:
            spawn = spawns[-int(r["entryorguid"])]
            for map_id in self.spawn_maps(spawn):
                self.smart_row(r, -self.spawn_guid(spawn["guid"], map_id))
        while self.actionlists_needed - self.actionlists_done:
            batch = self.actionlists_needed - self.actionlists_done
            self.actionlists_done |= batch
            for r in db.rows(db.CPP_DB, f"SELECT * FROM smart_scripts WHERE source_type = 9 AND entryorguid IN ({db.ids_in(batch)})"):
                self.smart_row(r, self.PATH + int(r["entryorguid"]))
        for t in self.ai_templates:
            t["AIName"] = "SmartAI"

    def smart_row(self, r, owner):
        v = {k: r[k] for k in r}
        v["entryorguid"] = owner
        event, action, target = int(r["event_type"]), int(r["action_type"]), int(r["target_type"])
        for i, kind in EVENT_PARAMS.get(event, {}).items():
            v[f"event_param{i}"] = self.smart_param(kind, r[f"event_param{i}"], None)
        if action == 114:                                   # (CPP's move by an offset: forward, here)
            v["action_type"], v["action_param1"] = 46, int(float(r["target_y"] or 0))
            v["target_type"], v["target_y"] = 1, 0
            target = 1
        for i, kind in ACTION_PARAMS.get(action, {}).items():
            v[f"action_param{i}"] = self.smart_param(kind, r[f"action_param{i}"], None)
        if action == 44:                                    # (CPP's phase id: the phase's bit, here)
            v["action_param1"], v["action_param2"] = self.phase_mask(r["action_param1"], 0), 0
        if target in (10, 14):                              # (a spawn by its guid: the nearest of its kind)
            entry = int(r["target_param2"] or 0)
            v["target_type"] = 19 if target == 10 else 20
            v["target_param1"] = self.creature_entry(entry) if target == 10 else self.object_entry(entry)
            v["target_param2"], v["target_param3"] = 100, 0
            if target == 10:
                self.need_creature(entry)
            else:
                self.need_object(entry)
        else:
            for i, kind in TARGET_PARAMS.get(target, {}).items():
                v[f"target_param{i}"] = self.smart_param(kind, r[f"target_param{i}"], None)
        for k in ("Difficulties", "event_param5", "action_param7", "target_param4"):
            v.pop(k, None)
        self.sql.add("smart_scripts", {c: v.get(c, 0) for c in self.ac_columns("smart_scripts")})

    def ac_columns(self, table):
        key = ("ac_columns", table)
        if key not in self.t:
            self.t[key] = db.column_names(db.AC_DB, table)
        return self.t[key]

    # --- Loot, wares, trainers ---------------------------------------------------------------------

    def loot(self, table, cata_id):
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = (table, cata_id)
        if key in self.done:
            return self.done[key]
        self.done[key] = self.ENTRY + cata_id
        for r in db.rows(db.CPP_DB, f"SELECT * FROM {table} WHERE Entry = {cata_id}"):
            if int(r.get("IsCurrency", 0) or 0):
                continue
            ref = int(r["Reference"] or 0)
            item = self.item(r["Item"]) if not ref else 0
            if not ref and not item:
                continue
            self.sql.add(table, {"Entry": self.ENTRY + cata_id, "Item": item if not ref else self.loot("reference_loot_template", ref),
                                 "Reference": self.loot("reference_loot_template", ref) if ref else 0, "Chance": r["Chance"],
                                 "QuestRequired": r["QuestRequired"], "LootMode": r["LootMode"], "GroupId": r["GroupId"],
                                 "MinCount": r["MinCount"], "MaxCount": r["MaxCount"], "Comment": r["Comment"]})
        return self.done[key]

    def vendors(self):
        for r in db.rows(db.CPP_DB, f"SELECT * FROM npc_vendor WHERE entry IN ({db.ids_in(self.creatures_done)}) AND type = 1"):
            item = self.item(r["item"])
            if item:
                self.sql.add("npc_vendor", {"entry": self.ENTRY + int(r["entry"]), "slot": r["slot"], "item": item,
                                            "maxcount": r["maxcount"], "incrtime": r["incrtime"], "ExtendedCost": 0, "VerifiedBuild": -15595})

    def trainers(self, templates):
        """Trainers teach 3.3.5a's own spells: each of Cataclysm's class trainers is one of the realm's
        own trainers of that class (the one with the most to teach), its profession trainers likewise."""
        theirs = {int(r["Id"]): r for r in db.rows(db.CPP_DB, "SELECT * FROM trainer")}
        ours = db.rows(db.AC_DB, "SELECT t.Id, t.Type, t.Requirement, COUNT(s.SpellId) n FROM trainer t "
                                 "LEFT JOIN trainer_spell s ON s.TrainerId = t.Id GROUP BY t.Id ORDER BY n DESC")
        defaults = {int(r["CreatureID"]): int(r["TrainerID"]) for r in db.rows(db.CPP_DB, "SELECT * FROM creature_trainer")} \
            if db.rows(db.CPP_DB, "SHOW TABLES LIKE 'creature_trainer'") else {}
        for e in templates:
            tid = defaults.get(e)
            if not tid or tid not in theirs:
                continue
            kind, requirement = int(theirs[tid]["Type"]), int(theirs[tid]["Requirement"])
            match = next((int(o["Id"]) for o in ours if int(o["Type"]) == kind and int(o["Requirement"]) == requirement), None)
            if match:
                self.sql.add("creature_default_trainer", {"CreatureId": self.ENTRY + e, "TrainerId": match})
            else:
                self.drop("trainer", tid)

    # --- Graveyards, area triggers, the areas' spells ----------------------------------------------

    def graveyards(self):
        areas = {int(r[0]) for r in self.out.rows.get("AreaTable", [])}
        safe = common.world_safe_locs(self.cache)
        for r in db.rows(db.CPP_DB, f"SELECT * FROM graveyard_zone WHERE GhostZone IN ({db.ids_in(areas)})"):
            loc = safe.get(int(r["ID"]))
            if loc is None or loc[0] not in (654, 648):
                continue
            maps = list(self.GILNEAS) if loc[0] == 654 else [loc[0]]
            for map_id in maps:
                gid = self.ENTRY + int(r["ID"]) + (self.GILNEAS.index(map_id) * 100_000 if map_id in self.GILNEAS else 0)
                if ("game_graveyard", gid) not in self.done:
                    self.done[("game_graveyard", gid)] = gid
                    self.sql.add("game_graveyard", {"ID": gid, "Map": map_id, "x": loc[1], "y": loc[2], "z": loc[3], "Comment": loc[5]})
                self.sql.add("graveyard_zone", {"ID": gid, "GhostZone": r["GhostZone"], "Faction": r["Faction"], "Comment": r["Comment"]})

    def area_triggers(self):
        """The maps' area triggers (3.3.5a's AreaTrigger table for the game, and the server's), with
        the quests they complete and the scripts they run."""
        maps = {654: list(self.GILNEAS), 648: [648]}
        found = []
        for r in self.table("AreaTrigger"):
            m = int(r["ContinentID"])
            if m not in maps:
                continue
            for map_id in maps[m]:
                aid = self.ids.new("AreaTrigger", int(r["ID"]) if map_id == m or map_id == 654 else None)
                found.append((int(r["ID"]), map_id, aid))
                values = {"ID": aid, "ContinentID": map_id, "Pos_0": float(r["Pos_0"]), "Pos_1": float(r["Pos_1"]), "Pos_2": float(r["Pos_2"]),
                          "Radius": float(r["Radius"]), "Box_length": float(r["Box_length"]), "Box_width": float(r["Box_width"]),
                          "Box_height": float(r["Box_height"]), "Box_yaw": float(r["Box_yaw"])}
                self.out.add("AreaTrigger", values)
                self.sql.add("areatrigger", {"entry": aid, "map": map_id, "x": values["Pos_0"], "y": values["Pos_1"], "z": values["Pos_2"],
                                             "radius": values["Radius"], "length": values["Box_length"], "width": values["Box_width"],
                                             "height": values["Box_height"], "orientation": values["Box_yaw"]})
        cata_ids = {c for c, _, _ in found}
        quests = {int(r["id"]): r for r in db.rows(db.CPP_DB, f"SELECT * FROM areatrigger_involvedrelation WHERE id IN ({db.ids_in(cata_ids)})")}
        scripts = {int(r["entry"]): r for r in db.rows(db.CPP_DB, f"SELECT * FROM areatrigger_scripts WHERE entry IN ({db.ids_in(cata_ids)})")}
        for cata, map_id, ours in found:
            if cata in quests:
                self.sql.add("areatrigger_involvedrelation", {"id": ours, "quest": self.quest_id(quests[cata]["quest"])})
            if cata in scripts:
                if scripts[cata]["ScriptName"] == "SmartTrigger":
                    for r in db.rows(db.CPP_DB, f"SELECT * FROM smart_scripts WHERE source_type = 2 AND entryorguid = {cata}"):
                        self.smart_row(r, ours)
                    self.sql.add("areatrigger_scripts", {"entry": ours, "ScriptName": "SmartTrigger"})
                elif self.script_name(scripts[cata]["ScriptName"], "area trigger", cata):
                    self.sql.add("areatrigger_scripts", {"entry": ours, "ScriptName": scripts[cata]["ScriptName"]})

    def area_spells(self):
        areas = {int(r[0]) for r in self.out.rows.get("AreaTable", [])}
        for r in db.rows(db.CPP_DB, f"SELECT * FROM spell_area WHERE area IN ({db.ids_in(areas)})"):
            spell = self.spell(r["spell"])
            if not spell:
                continue
            self.sql.add("spell_area", {"spell": spell, "area": int(r["area"]), "quest_start": self.quest_id(r["quest_start"]),
                                        "quest_end": self.quest_id(r["quest_end"]), "aura_spell": self.spell(r["aura_spell"]) if int(r["aura_spell"]) > 0 else -self.spell(-int(r["aura_spell"])) if int(r["aura_spell"]) < 0 else 0,
                                        "racemask": WORGEN | GOBLIN if not int(r["racemask"]) else self.races_of(0, int(r["racemask"])),
                                        "gender": r["gender"], "autocast": 1 if int(r["flags"]) & 1 else 0,
                                        "quest_start_status": r["quest_start_status"], "quest_end_status": r["quest_end_status"]})
        for cata_spell, start, end in LOST_ISLES_PHASES:
            spell = self.spell(cata_spell)
            if spell:
                self.sql.add("spell_area", {"spell": spell, "area": LOST_ISLES, "quest_start": self.quest_id(start) if start else 0,
                                            "quest_end": self.quest_id(end) if end else 0, "aura_spell": 0, "racemask": GOBLIN,
                                            "gender": 2, "autocast": 1, "quest_start_status": TAKEN if start else 0,
                                            "quest_end_status": NOT_REWARDED if end else 0})
        for cata_spell, start, end in GILNEAS_PHASES:
            spell = self.spell(cata_spell)
            for zone in GILNEAS_ZONES if spell else ():
                self.sql.add("spell_area", {"spell": spell, "area": zone, "quest_start": self.quest_id(start),
                                            "quest_end": self.quest_id(end), "aura_spell": 0, "racemask": WORGEN,
                                            "gender": 2, "autocast": 1, "quest_start_status": TAKEN,
                                            "quest_end_status": NOT_REWARDED})
