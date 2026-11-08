"""Cataclysm's items of the starting areas (quest items, rewards, loot, wares, what NPCs hold) in
AzerothCore's item_template, 3.3.5a's Item table (and the server's item_dbc) and its ItemDisplayInfo.

An item 3.3.5a has (the same id, the same name and kind) is 3.3.5a's own. A new one keeps Cataclysm's
id where nothing of 3.3.5a's or the realm's has it, else gets a new one. Its look: 3.3.5a's of that id
when 3.3.5a's is the same (its model and textures), else a new row through the converter (its rules for
the item looks: wotlkconv/db/itemdisplay.py), with the files and the names 3.3.5a loads them by.
"""
import os
import sys

import db

# Cataclysm's item stats 3.3.5a hasn't (mastery and the like): left out.
STATS_335 = set(range(0, 49))
# ItemEffect.TriggerType as item_template's spelltrigger (the same numbers: use, equip, chance on hit,
# soulstone, use with no delay, learn).
ITEM_SPELLS = 5


class ItemsMixin:
    def stock_items(self):
        if "stock_items" not in self.t:
            # (the realm's own items: never the starting areas' own, should a world they're in be read)
            self.t["stock_items"] = {int(r["entry"]): r for r in db.rows(
                db.AC_DB, "SELECT entry, name, class, subclass FROM item_template WHERE VerifiedBuild IS NULL OR VerifiedBuild <> -15595")}
        return self.t["stock_items"]

    def item(self, cata_id):
        """An item of Cataclysm's as one of the realm's."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = ("item", cata_id)
        if key in self.done:
            return self.done[key]
        sparse = self.by_id("ItemSparse").get(cata_id)
        item = self.by_id("Item").get(cata_id)
        if sparse is None or item is None:
            self.drop("item (not in Cataclysm's tables)", cata_id)
            self.done[key] = 0
            return 0
        stock = self.stock_items().get(cata_id)
        if stock is not None and stock["name"] == sparse["Display_lang"] and int(stock["class"]) == int(item["ClassID"]):
            self.done[key] = cata_id
            return cata_id
        taken = set(self.stock_items()) | self.ids.taken_ids("Item")
        our = cata_id if cata_id not in taken else self.ids.new("Item")
        self.ids.taken_ids("Item").add(our)
        self.done[key] = our
        display = self.item_look(self.item_display_of(cata_id))
        self.out.add("Item", {"ID": our, "ClassID": int(item["ClassID"]), "SubclassID": int(item["SubclassID"]),
                              "Sound_override_subclassID": int(item["Sound_override_subclassID"]), "Material": int(item["Material"]),
                              "DisplayInfoID": display, "InventoryType": int(item["InventoryType"]),
                              "SheatheType": int(item["SheatheType"])})
        self.sql.add("item_template", self.item_template(our, cata_id, sparse, item, display))
        return our

    def item_display_of(self, cata_id):
        if "item_display_of" not in self.t:
            appearance = {int(r["ID"]): int(r["ItemDisplayInfoID"]) for r in self.table("ItemAppearance")}
            index = {}
            for m in sorted(self.table("ItemModifiedAppearance"), key=lambda m: int(m.get("OrderIndex", 0) or 0)):
                index.setdefault(int(m["ItemID"]), appearance.get(int(m["ItemAppearanceID"]), 0))
            self.t["item_display_of"] = index
        return self.t["item_display_of"].get(cata_id, 0)

    def item_spells(self, cata_id):
        if "item_spells" not in self.t:
            index = {}
            for e in self.table("ItemEffect"):
                index.setdefault(int(e["ParentItemID"]), []).append(e)
            self.t["item_spells"] = index
        return sorted(self.t["item_spells"].get(cata_id, []), key=lambda e: int(e.get("LegacySlotIndex", 0) or 0))[:ITEM_SPELLS]

    def item_template(self, our, cata_id, s, item, display):
        v = {"entry": our, "class": int(item["ClassID"]), "subclass": int(item["SubclassID"]),
             "SoundOverrideSubclass": int(item["Sound_override_subclassID"]), "name": s["Display_lang"], "displayid": display,
             "Quality": int(s["OverallQualityID"]), "Flags": int(s["Flags_0"]) & 0xFFFFFFFF, "FlagsExtra": int(s["Flags_1"]) & 0xFFFFFFFF,
             "BuyCount": max(1, int(s["VendorStackCount"])), "BuyPrice": int(s["BuyPrice"]), "SellPrice": int(s["SellPrice"]),
             "InventoryType": int(item["InventoryType"]), "AllowableClass": int(s["AllowableClass"]),
             "AllowableRace": self.race_mask_any(int(s["AllowableRace"])), "ItemLevel": int(s["ItemLevel"]),
             "RequiredLevel": int(s["RequiredLevel"]), "RequiredSkill": int(s["RequiredSkill"]),
             "RequiredSkillRank": int(s["RequiredSkillRank"]), "requiredspell": 0, "requiredhonorrank": 0, "RequiredCityRank": 0,
             "RequiredReputationFaction": self.faction(s["MinFactionID"]) if int(s["MinFactionID"]) else 0,
             "RequiredReputationRank": int(s["MinReputation"]), "maxcount": int(s["MaxCount"]), "stackable": int(s["Stackable"]),
             "ContainerSlots": int(s["ContainerSlots"]), "ScalingStatDistribution": 0, "ScalingStatValue": 0,
             "armor": int(s["Resistances_0"]), "holy_res": int(s["Resistances_1"]), "fire_res": int(s["Resistances_2"]),
             "nature_res": int(s["Resistances_3"]), "frost_res": int(s["Resistances_4"]), "shadow_res": int(s["Resistances_5"]),
             "arcane_res": int(s["Resistances_6"]), "delay": int(s["ItemDelay"]), "ammo_type": int(s["AmmunitionType"]),
             "RangedModRange": float(s["ItemRange"]), "bonding": int(s["Bonding"]), "description": s["Description_lang"],
             "PageText": 0, "LanguageID": int(s["LanguageID"]), "PageMaterial": int(s["PageMaterialID"]),
             "startquest": self.quest_id(s["StartQuestID"]) if int(s["StartQuestID"]) else 0,
             "lockid": 0, "Material": int(s["Material"]), "sheath": int(s["SheatheType"]), "RandomProperty": 0, "RandomSuffix": 0,
             "block": 0, "itemset": 0, "MaxDurability": int(s["MaxDurability"]), "area": 0, "Map": 0, "BagFamily": int(s["BagFamily"]),
             "TotemCategory": 0, "socketBonus": 0, "GemProperties": 0, "RequiredDisenchantSkill": -1, "ArmorDamageModifier": 0.0,
             "duration": int(s["DurationInInventory"]), "ItemLimitCategory": 0, "HolidayId": 0, "ScriptName": "", "DisenchantID": 0,
             "FoodType": 0, "minMoneyLoot": 0, "maxMoneyLoot": 0, "flagsCustom": 0, "VerifiedBuild": -15595}
        if int(s["PageID"]):
            self.drop("item page text", cata_id)
        if int(s["LockID"]):
            self.drop("item lock", cata_id)
        stats = []
        for i in range(10):
            stat, amount = int(s[f"StatModifier_bonusStat_{i}"]), int(s[f"StatModifier_bonusAmount_{i}"])
            if stat >= 0 and amount and stat in STATS_335:
                stats.append((stat, amount))
        for i in range(10):
            stat, amount = stats[i] if i < len(stats) else (0, 0)
            v[f"stat_type{i + 1}"], v[f"stat_value{i + 1}"] = stat, amount
        for i in range(2):
            v[f"dmg_min{i + 1}"] = float(s[f"MinDamage_{i}"])
            v[f"dmg_max{i + 1}"] = float(s[f"MaxDamage_{i}"])
            v[f"dmg_type{i + 1}"] = int(item[f"DamageType_{i}"]) if f"DamageType_{i}" in item else int(s["DamageType"]) if i == 0 else 0
        effects = self.item_spells(cata_id)
        for i in range(ITEM_SPELLS):
            e = effects[i] if i < len(effects) else None
            v[f"spellid_{i + 1}"] = self.spell(e["SpellID"]) if e else 0
            v[f"spelltrigger_{i + 1}"] = int(e["TriggerType"]) if e else 0
            v[f"spellcharges_{i + 1}"] = int(e["Charges"]) if e else 0
            v[f"spellppmRate_{i + 1}"] = 0.0
            v[f"spellcooldown_{i + 1}"] = int(e["CoolDownMSec"]) if e else -1
            v[f"spellcategory_{i + 1}"] = 0
            v[f"spellcategorycooldown_{i + 1}"] = int(e["CategoryCoolDownMSec"]) if e else -1
        for i in range(3):
            v[f"socketColor_{i + 1}"], v[f"socketContent_{i + 1}"] = 0, 0
        return v

    def race_mask_any(self, mask):
        """A Cataclysm race mask as 3.3.5a's (-1 and every race stay every race)."""
        mask &= 0xFFFFFFFF
        if mask in (0, 0xFFFFFFFF) or mask & 0x7FFF == 0x7FFF:
            return -1
        from build_world import race_mask
        return race_mask(mask)

    # --- Item looks --------------------------------------------------------------------------------

    def resolver(self):
        """The converter's own ItemDisplayInfo rules over Cataclysm Classic's tables (in-process: the
        files and the names 3.3.5a loads them by)."""
        if "resolver" not in self.t:
            sys.path.insert(0, self.converter_src)
            from wotlkconv.db.dbd import DbdIndex
            from wotlkconv.db.itemdisplay import ItemDisplayResolver, REQUIRED_TABLES
            from wotlkconv.db.tables import TableProvider
            from wotlkconv.listfile import Listfile
            for name in REQUIRED_TABLES:
                self.db2(name)
            listfile = Listfile.load(self.listfile_path)
            tables = TableProvider(DbdIndex(self.dbd), listfile=listfile, directory=os.path.join(self.cache, "db2"))
            self.t["resolver"] = ItemDisplayResolver(tables, listfile)
        return self.t["resolver"]

    def item_look(self, cata_id):
        """An ItemDisplayInfo (an item's look; an NPC's clothes): 3.3.5a's of that id when it's the same
        model and textures, else new (converted) with its files."""
        cata_id = int(cata_id or 0)
        if cata_id <= 0:
            return 0
        key = ("ItemDisplayInfo", cata_id)
        if key in self.done:
            return self.done[key]
        row = self.convert_rows("ItemDisplayInfo", [cata_id]).get(cata_id)
        if row is None:
            self.drop("item display", cata_id)
            self.done[key] = 0
            return 0
        values = self.as_dict("ItemDisplayInfo", row)
        stock = self.ids.stock_rows("ItemDisplayInfo").get(cata_id)
        columns = self.columns("ItemDisplayInfo")
        names = [c for c in columns if c.startswith(("ModelName", "ModelTexture", "Texture_"))]
        if stock is not None and all(str(stock[columns.index(c)]).lower() == str(values[c]).lower() for c in names):
            self.done[key] = cata_id
            return cata_id
        values["ID"] = self.ids.new("ItemDisplayInfo", cata_id)
        values["SpellVisualID"] = values.get("SpellVisualID", 0) if values.get("SpellVisualID", 0) in self.ids.stock_rows("SpellVisual") else 0
        values["ParticleColorID"] = 0
        self.put("ItemDisplayInfo", values)
        self.item_look_files(cata_id)
        self.done[key] = values["ID"]
        return values["ID"]

    def item_look_files(self, cata_id):
        """The files of an item look, and the other names 3.3.5a loads some of them by (a helmet's
        model by race and sex, a model's texture beside it, the icon, the armour's textures by body
        part): wotlkconv's own rules."""
        r = self.resolver()
        row = r.tables.row("ItemDisplayInfo", cata_id)
        if row is None:
            return
        row = {**row, "ID": cata_id}
        own, alias = [], []
        for index in (0, 1):
            resources = row.get("ModelResourcesID") or [0, 0]
            resource = int(resources[index]) if index < len(resources) else 0
            if resource and r.model_name(row, index):
                own += [fid for fid, _, _ in r._model_files(resource)]
                alias += r._model(row, index)[1]
            name, fid, path = r._model_texture(row, index)
            if name:
                own.append(fid)
                alias.append((fid, f"{r._model_folder(row, index)}\\{name}.blp"))
        name, fid, path = r._icon(row)
        if name:
            own.append(fid)
            alias.append((fid, f"interface\\icons\\{name}.blp"))
        sections = ["armuppertexture", "armlowertexture", "handtexture", "torsouppertexture", "torsolowertexture",
                    "leguppertexture", "leglowertexture", "foottexture"]
        for section in range(8):
            for material in self.materials_of(cata_id, section):
                base = r._material_base(material)
                for fid, path, component in r._component_files(material):
                    own.append(fid)
                    letter = {0: "m", 1: "f", 3: "u"}.get(int(component.get("GenderIndex", -1)))
                    if base and letter:
                        alias.append((fid, f"item\\texturecomponents\\{sections[base[0]]}\\{base[1]}_{letter}.blp"))
        for fid in own:
            if fid and int(fid) in self.names:
                self.add_file(fid, "model" if self.names[int(fid)].endswith(".m2") else "texture")
        for fid, path in alias:
            if not fid or int(fid) not in self.names:
                continue
            path = path.replace("\\", "/").lower()
            if path != self.names[int(fid)]:
                self.add_file(fid, "model" if path.endswith(".m2") else "texture")
                self.aliases.setdefault(int(fid), set()).add(path)

    def materials_of(self, cata_id, section):
        if "materials_of" not in self.t:
            index = {}
            for m in self.table("ItemDisplayInfoMaterialRes"):
                index.setdefault((int(m["ItemDisplayInfoID"]), int(m["ComponentSection"])), []).append(int(m["MaterialResourcesID"]))
            self.t["materials_of"] = index
        return self.t["materials_of"].get((cata_id, section), [])
