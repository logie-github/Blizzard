"""QuestieDB's Forever database (github.com/Questie/QuestieDB): its raw data (data/Forever) with its
generated delta-base, trace and authored Forever corrections on top, in that order, as its own
loader applies them. Read as data by lualit.py; no Lua is run."""
import os
import re

import lualit


def read(qdb):
    """Forever's quests, NPCs, items and objects: QuestieDB's raw data with its generated delta-base,
    trace and authored Forever corrections on top, in that order (as its own loader applies them)."""
    def enum(path, name):
        text = open(path, encoding="utf-8").read()
        m = re.search(r"constants\.%s\s*=\s*\{" % name, text)
        return lualit.to_py(lualit.Parser(lualit.tokens(text[m.end() - 1:]), lambda n: ("sym", n)).table())

    zones = enum(os.path.join(qdb, "src/corrections/enum/zones.lua"), "zoneIDs")
    factions = enum(os.path.join(qdb, "src/corrections/enum/factions.lua"), "factionIDs")
    race = {"NONE": 0, "HUMAN": 1, "ORC": 2, "DWARF": 4, "NIGHT_ELF": 8, "UNDEAD": 16, "TAUREN": 32, "GNOME": 64, "TROLL": 128,
            "SKYBORNE_ALLIANCE": 1 << 32, "SKYBORNE_HORDE": 1 << 33}
    race["ALL_ALLIANCE"] = 1 + 4 + 8 + 64 + (1 << 32)
    race["ALL_HORDE"] = 2 + 16 + 32 + 128 + (1 << 33)
    klass = dict(NONE=0, WARRIOR=1, PALADIN=2, HUNTER=4, ROGUE=8, PRIEST=16, DEATH_KNIGHT=32, SHAMAN=64, MAGE=128,
                 WARLOCK=256, MONK=512, DRUID=1024, ALL_CLASSES=1503)

    def resolve(name):
        parts = name.split(".")
        group, last = (parts[-2] if len(parts) > 1 else parts[0]), parts[-1]
        if group in ("questKeys", "npcKeys", "itemKeys", "objectKeys"):
            return "@" + last
        if group in ("raceIDs", "raceKeys") and last in race:
            return race[last]
        if group in ("classIDs", "classKeys") and last in klass:
            return klass[last]
        if group == "zoneIDs" and isinstance(zones.get(last), int):
            return zones[last]
        if group == "factionIDs" and isinstance(factions.get(last), int):
            return factions[last]
        return ("sym", name)

    def keymap(text, kind):
        m = re.search(r"QuestieDB\.%sKeys\s*=\s*\{(.*?)\n\}" % kind, text, re.S)
        return {int(i): k for k, i in re.findall(r"^\s*\['(\w+)'\]\s*=\s*(\d+)", m.group(1), re.M)}

    def corrections(path):
        text = open(path, encoding="utf-8").read()
        return lualit.to_py(lualit.parse_return_table(text, resolve, after=":Load()"))

    def merge(cur, value, op):
        if isinstance(value, dict):
            value = [value.get(i) for i in range(1, max(value) + 1)]
        cur = list(cur or [])
        grouped = all(x is None or isinstance(x, list) for x in value) and any(isinstance(x, list) for x in value)
        if grouped and all(x is None or isinstance(x, list) for x in cur):
            cur += [None] * (len(value) - len(cur))
            for i, group in enumerate(value):
                if group is None:
                    continue
                have = list(cur[i] or [])
                have = have + [x for x in group if x not in have] if op == "add" else [x for x in have if x not in group]
                cur[i] = have
            return cur
        return cur + [x for x in value if x not in cur] if op == "add" else [x for x in cur if x not in value]

    db = {}
    for kind, name, fixes in (("quest", "Quest", "Quest"), ("npc", "Npc", "NPC"), ("item", "Item", "Item"), ("object", "Object", "Object")):
        path = os.path.join(qdb, "data/Forever/forever%sDB.lua" % name)
        text = open(path, encoding="utf-8").read()
        keys = keymap(text, kind)
        m = re.search(r"QuestieDB\.%sData\s*=\s*\[(=*)\[" % kind, text)
        body = text[m.end(): text.index("]%s]" % m.group(1), m.end())]
        raw = lualit.to_py(lualit.parse_return_table(body, resolve))
        rows = {}
        for eid, row in (raw.items() if isinstance(raw, dict) else enumerate(raw, 1)):
            if row is None:
                continue
            if isinstance(row, dict):
                row = [row.get(i) for i in range(1, max(row) + 1)] if row else []
            rows[eid] = {keys[i + 1]: v for i, v in enumerate(row) if v is not None and i + 1 in keys}
        for path in ("src/corrections/Forever/generated/foreverBase%s.lua" % name,
                     "src/corrections/Forever/traces/forever%sTraces.lua" % name,
                     "src/corrections/Forever/forever%sFixes.lua" % fixes):
            for eid, fix in corrections(os.path.join(qdb, path)).items():
                if not isinstance(fix, dict):
                    continue
                row = rows.setdefault(eid, {})
                for key, value in fix.items():
                    if not (isinstance(key, str) and key.startswith("@")):
                        continue
                    key = key[1:]
                    if key.endswith("_add") or key.endswith("_remove"):
                        field, op = key.rsplit("_", 1)
                        row[field] = merge(row.get(field), value, op)
                    else:
                        row[key] = value
        db[kind] = rows
    return db
