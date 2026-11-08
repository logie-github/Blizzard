#!/usr/bin/env python3
"""WoW: Forever's new quests in the old zones, for the 3.3.5 world: the quests, their new people
and creatures (each drawn as the 3.3.5 creature nearest it in kind), their items and rewards.

    python3 tools/forever.py import QUESTIEDB_DIR WORLD_SQL_DIR SERVER_DATA_DIR CACHE_DIR
        Reads QuestieDB's Forever database (questiedb.py), picks the quests, and fetches into
        CACHE_DIR (kept between runs): each quest's page on foreverchanges.pro (its words, counts,
        rewards, money, experience, reputation: Wowhead's Forever database as that site shows
        it), Wowhead's tooltips of the new NPCs and reward items, and the Forever client's Item
        and ItemSparse tables (wago.tools). Writes data/forever/quests.json (the quests, their
        NPCs with their spawns in the world's coordinates, their items, the rewards) and
        data/forever/report.json (every other new quest and why it isn't here).

    python3 tools/forever.py build SERVER_DATA_DIR WORLD_SQL_DIR
        Writes data/sql/chromiecraft/world/forever_quests.sql from data/forever/quests.json and
        experience.json (wow4ever.quest's experience, where the page has none).

SERVER_DATA_DIR: the server data (dbc and maps folders; the data.zip in warcraft/server-data.env);
WORLD_SQL_DIR: the core's data/sql/base/db_world at the realm's commit (warcraft/server-version.env).
Both outputs are committed; run the tool again after changing it or its data.
"""
import csv
import json
import math
import os
import re
import statistics
import struct
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import foreverchanges  # noqa: E402
import questiedb  # noqa: E402
import sqlrows  # noqa: E402
import terrain  # noqa: E402
import wowhead  # noqa: E402

MODULE = os.path.dirname(HERE)
DATA = os.path.join(MODULE, "data", "forever")
SQL_OUT = os.path.join(MODULE, "data", "sql", "chromiecraft", "world", "forever_quests.sql")

FIRST_FOREVER_ID = 86000        # Forever's own quests; below are Classic Era's and Season of Discovery's
FOREVER_BUILD = "1.60.1.70532"  # the client foreverchanges.pro's pages and wago.tools' tables are of
FIRST_GUID = 8600000            # the new creatures' spawns (the core's go to 5.3 million, Wrath Remix's are 7.7 million)
# Forever's new zones and dungeons (the user: "don't worry about the new zone ones"), and the kinds
# of quest that aren't for this world: as foreverchanges.pro files them.
NEW_AREAS = {"Zephras Isle", "Shen'dralas", "Riverglades", "The Hall of Thanes", "Ruins of Lordaeron",
             "Excavation Site: Wetlands", "City of Dalaran", "Darkspear Islands"}
NOT_HERE = {"Crafting": "a Craftsman's Writ (Forever's crafting orders)", "Camping": "Forever's Camping profession",
            "Fishing": "Forever's fishing contest", "Lunar Festival": "a holiday quest of Forever's",
            "Special": "not a quest to play", "Invasion": "Forever's invasions"}
CLASS_AREAS = {"Warrior", "Paladin", "Hunter", "Rogue", "Priest", "Shaman", "Mage", "Warlock", "Druid", "Night Elf"}
# Zones whose map Forever redrew: QuestieDB holds back the new spawns there (their coordinates are
# on Forever's map, not 3.3.5's).
CHANGED_FRAMES = {44, 139, 215, 1519}
# Quests that pass the checks below but can't be made from the data as it is.
LEFT_OUT = {
    92743: "needs a Conqueror's Crown that QuestieDB doesn't list, and Magram standing",
    93928: "the mouse's cookie isn't in the data (a scripted hand-in)",
    98071: "its objective (the hops from Dun Garok) isn't in the data",
    98221: "its objective (the attack plans to destroy) isn't in the data",
    95737: "leads to Excavation Site: Wetlands, a new dungeon",
    99108: "duels with other players",
    99267: "no objective, giver's words or level in the data",
}

# Forever's race bits (QuestieDB: requiredRaces) and the 3.3.5 races each opens here. Races the
# 3.3.5 realm adds go with the race whose start they take: the Skyborne of the High Order with the
# Humans (mod-skyborne), the Windshapers and the Zandalari with the Tauren; the Draenei, void elves
# and Lightforged with the Night Elves (the Alliance's other Kalimdor race), the blood elves and the
# nightborne with the Forsaken.
SKYBORNE_A, SKYBORNE_H = 1 << 12, 1 << 13                 # races 13, 14 (mod-skyborne)
VOIDELF, NIGHTBORNE, LIGHTFORGED, ZANDALARI = 1 << 14, 1 << 15, 1 << 16, 1 << 17   # mod-allied-races
RACES = {
    1: 1 | SKYBORNE_A,                                     # Human
    2: 2,                                                  # Orc
    4: 4,                                                  # Dwarf
    8: 8 | 1024 | VOIDELF | LIGHTFORGED,                   # Night Elf (Draenei, void elves, Lightforged)
    16: 16 | 512 | NIGHTBORNE,                             # Undead (blood elves, nightborne)
    32: 32 | SKYBORNE_H | ZANDALARI,                       # Tauren
    64: 64,                                                # Gnome
    128: 128,                                              # Troll
    1 << 32: SKYBORNE_A,                                   # Forever's Skyborne of the High Order
    1 << 33: SKYBORNE_H,                                   # and Windshapers
}
ALL_RACES = 0
for bits in RACES.values():
    ALL_RACES |= bits

QUEST_FLAGS_SHARABLE = 8
ITEM_BIND_PICKUP, ITEM_BIND_QUEST = 1, 4
# Who a new NPC's faction is friendly to (QuestieDB: friendlyToFaction), where the look it takes
# after isn't: Stormwind's, Orgrimmar's, everyone's; and a monster's for the hostile.
FACTIONS = {"A": 12, "H": 29, "AH": 35, "": 14}
# What a friendly person "drops" in Forever's data (QuestieDB lists an item handed over as a drop: Executor
# Zygand's reports from Deathguard Dillinger, Deathguard Kristof and Gordo) is asked of them instead: an
# option in their menu while the quest is in the log and the item isn't in the bags (the gossip menus and
# options, their conditions, and the creature's SmartAI giving it: ids from these).
GIVE_MENU = 8600000             # a menu (and its words) for one who has none
GIVE_OPTION = 860               # the options' ids in any menu (the core's own go to 37476 in other numbers)
GIVE_EVENT = 860                # the SmartAI events' ids
# The hand-in words for a quest whose data has none (the user: "just make something simple up").
NO_HAND_IN = "Hand in the quest."


def table(world, name):
    return sqlrows.table(os.path.join(world, name + ".sql"))


def dbc(path):
    """A DBC file's records as tuples of uint32 and its string block."""
    with open(path, "rb") as f:
        data = f.read()
    magic, count, fields, size, strsize = struct.unpack("<4s4I", data[:20])
    assert magic == b"WDBC" and size == fields * 4, path
    rows = [struct.unpack_from("<%dI" % fields, data, 20 + i * size) for i in range(count)]
    return rows, data[20 + count * size:]


def dbc_string(block, offset):
    return block[offset:block.index(b"\0", offset)].decode("utf-8", "replace")


def world_maps(dbc_dir):
    """Each zone's map and its bounds on the world (WorldMapArea.dbc): left, right, top, bottom."""
    with open(os.path.join(dbc_dir, "WorldMapArea.dbc"), "rb") as f:
        data = f.read()
    _, count, fields, size, _ = struct.unpack("<4s4I", data[:20])
    out = {}
    for i in range(count):
        _, map_id, area = struct.unpack_from("<3I", data, 20 + i * size)
        if area:
            out[area] = (map_id, struct.unpack_from("<4f", data, 20 + i * size + 16))
    return out


def group(lst, i):
    return list(lst[i] or []) if lst and len(lst) > i and lst[i] else []


def first_ids(entries):
    return [e[0] if isinstance(e, list) else e for e in entries]


def wago_table(name, cache):
    """One of the Forever client's tables (wago.tools' CSV of it), by its first column."""
    path = os.path.join(cache, "%s-%s.csv" % (name, FOREVER_BUILD))
    if not os.path.exists(path):
        url = "https://wago.tools/db2/%s/csv?build=%s" % (name, FOREVER_BUILD)
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": wowhead.USER_AGENT}), timeout=300) as r:
            data = r.read()
        with open(path, "wb") as f:
            f.write(data)
    with open(path, encoding="utf-8", newline="") as f:
        return {int(r["ID"]): r for r in csv.DictReader(f)}


# --- import -----------------------------------------------------------------------------------

def import_(qdb, world, server_data, cache):
    db = questiedb.read(qdb)
    Q, I, N = db["quest"], db["item"], db["npc"]
    _, quests = table(world, "quest_template")
    core_quests = {int(q["ID"]) for q in quests}
    _, creatures = table(world, "creature")
    spawned = {int(c["id1"]) for c in creatures}
    _, templates = table(world, "creature_template")
    core_creatures = {int(c["entry"]) for c in templates}
    _, items = table(world, "item_template")
    core_items = {int(i["entry"]) for i in items}
    _, objects = table(world, "gameobject_template")
    core_objects = {int(o["entry"]) for o in objects}
    maps = world_maps(os.path.join(server_data, "dbc"))
    spell_rows, _ = dbc(os.path.join(server_data, "dbc", "Spell.dbc"))
    core_spells = {r[0] for r in spell_rows}

    new = sorted(q for q in Q if q >= FIRST_FOREVER_ID and q not in core_quests)
    foreverchanges.fetch(new, cache)
    pages = {q: foreverchanges.parse(os.path.join(cache, "%d.html" % q)) for q in new}

    def spawns(n):
        """A new NPC's spawns in the world's coordinates: (map, x, y), where 3.3.5 has the zone."""
        raw = N.get(n, {}).get("spawns") or {}
        if isinstance(raw, list):
            raw = {i + 1: v for i, v in enumerate(raw) if v}
        out = []
        for zone, points in sorted((int(z), v) for z, v in raw.items()):
            if zone not in maps or zone in CHANGED_FRAMES:
                continue
            map_id, (left, right, top, bottom) = maps[zone]
            for p in points or []:
                if isinstance(p, list) and len(p) >= 2 and p[0] >= 0:
                    out.append([map_id, round(top - p[1] / 100 * (top - bottom), 2), round(left - p[0] / 100 * (left - right), 2)])
        return out

    def placeable(n):
        return n in spawned or (n not in core_creatures and bool(spawns(n)))

    def problems(qid):
        q, page = Q[qid], pages[qid]
        out = []
        if not page:
            return ["foreverchanges.pro has no page for it (its text)"]
        area = page["category"]
        if area in NEW_AREAS:
            out.append("in %s, one of Forever's new zones and dungeons" % area)
        elif area in NOT_HERE:
            out.append(NOT_HERE[area])
        elif area in CLASS_AREAS or q.get("requiredClasses"):
            out.append("a class or race quest (3.3.5's class training has its own)")
        name = q.get("name") or ""
        if re.search(r"UNUSED|zzOLD|^Legacy Reward", name):
            out.append("not a quest to play (%s)" % name)
        start, end = q.get("startedBy") or [], q.get("finishedBy") or []
        starters, start_objects, start_items = group(start, 0), group(start, 1), group(start, 2)
        enders, end_objects = group(end, 0), group(end, 1)
        if not (starters or start_objects or start_items):
            out.append("nobody starts it in the data")
        if not (enders or end_objects):
            out.append("nobody ends it in the data")
        lost = [n for n in starters + enders if not placeable(n)]
        if lost:
            out.append("people the data has no place for in the old zones: %s" % lost)
        if [o for o in start_objects + end_objects if o not in core_objects]:
            out.append("new objects")
        if start_items and not starters and not start_objects:
            sources = [d for i in start_items for d in (I.get(i, {}).get("npcDrops") or [])]
            if not any(placeable(d) for d in sources):
                out.append("starts from an item nothing in the old zones drops")
        objectives = q.get("objectives") or []
        if any(isinstance(c, list) and len(c) > 2 and c[2] for c in group(objectives, 0)):
            out.append("an objective done by an event or a talk (a script)")
        if [c for c in first_ids(group(objectives, 0)) if not placeable(c)]:
            out.append("creatures to kill the data has no place for in the old zones")
        if group(objectives, 1):
            out.append("objects to use")
        for item in first_ids(group(objectives, 2)):
            if item in core_items or item == q.get("sourceItemId"):
                continue
            drops = I.get(item, {}).get("npcDrops") or []
            if not drops:
                out.append("an item to collect that no creature drops in the data (%d)" % item)
            elif not any(placeable(d) for d in drops):
                out.append("an item to collect from creatures the data has no place for (%d)" % item)
        if len(objectives) > 3 and objectives[3]:
            out.append("a reputation objective")
        if len(objectives) > 4 and objectives[4]:
            out.append("kill credit (a script)")
        if len(objectives) > 5 and objectives[5]:
            out.append("a spell to cast (a script)")
        if q.get("triggerEnd"):
            out.append("a place to explore (a script)")
        if q.get("extraObjectives"):
            out.append("special objectives (a script)")
        if q.get("requiredSkill") or q.get("requiredRanks"):
            out.append("a profession requirement")
        if qid in LEFT_OUT:
            out.append(LEFT_OUT[qid])
        return out

    why = {q: problems(q) for q in new}
    picked = {q for q in new if not why[q]}
    # A quest that needs another first goes only with it (or after one the core has).
    grew = True
    while grew:
        grew = False
        for q in sorted(picked):
            pre = (Q[q].get("preQuestSingle") or []) + (Q[q].get("preQuestGroup") or [])
            missing = [p for p in pre if p not in core_quests and p not in picked]
            if missing:
                picked.discard(q)
                why[q] = ["needs %s first, which isn't here" % missing]
                grew = True

    # The new NPCs: givers, enders, the creatures to kill, and those that drop the items wanted
    # (only where no creature of the core's does).
    wanted = set()
    used_items = set()
    for qid in picked:
        q = Q[qid]
        wanted.update(group(q.get("startedBy"), 0) + group(q.get("finishedBy"), 0) + first_ids(group(q.get("objectives"), 0)))
        for i in first_ids(group(q.get("objectives"), 2)) + group(q.get("startedBy"), 2):
            used_items.add(i)
            drops = I.get(i, {}).get("npcDrops") or []
            if i not in core_items and not any(d in spawned for d in drops):
                wanted.update(d for d in drops if placeable(d))
        if q.get("sourceItemId"):
            used_items.add(q["sourceItemId"])
    new_npcs = sorted(n for n in wanted if n not in spawned)
    # Whose side each new NPC is on. A giver or ender the data leaves on no side is on its quests'
    # side; a creature to kill or loot is no friend of the side its quests are for.
    alliance = 1 + 4 + 8 + 64 + (1 << 32)
    horde = 2 + 16 + 32 + 128 + (1 << 33)

    def side(q):
        mask = Q[q].get("requiredRaces") or 0
        return "A" if mask and not mask & horde else "H" if mask and not mask & alliance else "AH"
    serves, fights = {}, {}
    for qid in picked:
        q = Q[qid]
        for n in group(q.get("startedBy"), 0) + group(q.get("finishedBy"), 0):
            serves.setdefault(n, set()).update(side(qid))
        targets = first_ids(group(q.get("objectives"), 0))
        for i in first_ids(group(q.get("objectives"), 2)) + group(q.get("startedBy"), 2):
            targets += I.get(i, {}).get("npcDrops") or []
        for n in targets:
            fights.setdefault(n, set()).update(side(qid))
    wowhead.fetch("npc", new_npcs, cache)
    npcs = {}
    for n in sorted(wanted):
        if n in spawned:
            npcs[str(n)] = {"zoneID": N.get(n, {}).get("zoneID")}
            continue
        row = N.get(n, {})
        tip = wowhead.load("npc", n, cache)
        about = wowhead.npc(tip) if tip else {"type": 0, "family": "", "rank": 0, "level": None}
        level = about["level"] or [row.get("minLevel") or 1, row.get("maxLevel") or row.get("minLevel") or 1]
        npcs[str(n)] = {"new": True, "name": row.get("name") or (tip or {}).get("name"), "subName": row.get("subName") or "",
                        "level": [row.get("minLevel") or level[0], row.get("maxLevel") or level[1]],
                        "type": about["type"], "family": about["family"] if about["type"] in (1, 8) else "",
                        "rank": about["rank"],
                        "friendly": "".join(c for c in (row.get("friendlyToFaction") or "".join(sorted(serves.get(n, ""))))
                                            if n in serves or c not in fights.get(n, set())),
                        "zoneID": row.get("zoneID"), "spawns": spawns(n)}
    clash = [n for n in new_npcs if n in core_creatures]
    assert not clash, "new NPCs whose ids the core has: %s" % clash

    # The new items: the quest items (collected, carried, started from) and the rewards.
    out_items = {}
    for i in sorted(used_items):
        if i in core_items:
            continue
        row = I.get(i, {})
        drops = [d for d in row.get("npcDrops") or [] if d in spawned or str(d) in npcs]
        out_items[str(i)] = {"name": row.get("name"), "drops": drops, "startQuest": row.get("startQuest") or 0}
    for qid in picked:
        for i, icon in pages[qid]["icons"].items():
            if i in out_items:
                out_items[i]["icon"] = icon
    reward_ids = sorted({i for q in picked for i, _ in pages[q]["reward_items"] + pages[q]["reward_choice"]} - core_items)
    wowhead.fetch("item", reward_ids, cache)
    wago_items, wago_sparse = wago_table("Item", cache), wago_table("ItemSparse", cache)
    rewards, unusable = {}, {}
    for i in reward_ids:
        tip = wowhead.load("item", i, cache)
        base, sparse = wago_items.get(i), wago_sparse.get(i)
        if not tip or not base or not sparse:
            unusable[i] = "neither Wowhead's tooltip nor the client's tables have it"
            continue
        r = wowhead.item(tip)
        missing = [s for s in r["use"] if s not in core_spells]
        if missing:
            unusable[i] = "%s: what it does (spell %s) isn't in 3.3.5" % (r["name"], missing)
            continue
        r.update({"class": int(base["ClassID"]), "subclass": int(base["SubclassID"]), "material": int(base["Material"]),
                  "inventory": int(base["InventoryType"]), "sheath": int(base["SheatheType"]),
                  "quality": int(sparse["OverallQualityID"]), "item_level": int(sparse["ItemLevel"]) or r["item_level"],
                  "required_level": int(sparse["RequiredLevel"]), "bonding": int(sparse["Bonding"]),
                  "buy": int(sparse["BuyPrice"]), "sell": int(sparse["SellPrice"]), "stack": int(sparse["Stackable"]) or 1,
                  "maxcount": int(sparse["MaxCount"]), "bag_slots": int(sparse["ContainerSlots"]),
                  "delay": int(sparse["ItemDelay"]), "allowable_class": int(sparse["AllowableClass"]),
                  "allowable_race": int(sparse["AllowableRace_0"]), "start_quest": int(sparse["StartQuestID"])})
        rewards[str(i)] = r
    for qid in picked:
        page = pages[qid]
        for key in ("reward_items", "reward_choice"):
            page[key] = [[i, c] for i, c in page[key] if i in core_items or str(i) in rewards]

    keep = ("name", "startedBy", "finishedBy", "requiredLevel", "questLevel", "requiredRaces", "objectives",
            "sourceItemId", "preQuestSingle", "preQuestGroup", "exclusiveTo", "zoneOrSort", "breadcrumbForQuestId")
    out_quests = {}
    for q in sorted(picked):
        row = {k: Q[q][k] for k in keep if k in Q[q]}
        page = dict(pages[q])
        page.pop("icons")
        row["page"] = page
        out_quests[str(q)] = row
    head = ("WoW: Forever's new quests in the old zones (tools/forever.py import). Who gives and ends them, objectives, "
            "item sources, chains, races and the new NPCs' places: QuestieDB's Forever database (github.com/Questie/QuestieDB), "
            "the places in the world's coordinates. Each quest's page: its words, counts, rewards, money, experience and "
            "reputation from foreverchanges.pro (Wowhead's Forever database). The new NPCs' type, family and rank and the "
            "rewards' stats: Wowhead's tooltips; the rewards' slots, binding and prices: the Forever client's Item and "
            "ItemSparse (wago.tools, build %s). Quest text (c) Blizzard Entertainment." % FOREVER_BUILD)
    with open(os.path.join(DATA, "quests.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"_about": head, "quests": out_quests, "items": out_items, "rewards": rewards, "npcs": npcs}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    report = {"_about": "Forever's new quests (ids %d and up, not in the core) left out, and why; reward items left out." % FIRST_FOREVER_ID,
              "picked": len(picked), "new": len(new),
              "left_out": {str(q): {"name": Q[q].get("name"), "area": (pages[q] or {}).get("category"), "why": why[q]}
                           for q in new if q not in picked},
              "rewards_left_out": {str(i): w for i, w in sorted(unusable.items())}}
    with open(os.path.join(DATA, "report.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("%d of Forever's %d new quests picked; %d new NPCs, %d new items, %d rewards (%d left out)" % (
        len(picked), len(new), len(new_npcs), len(out_items), len(rewards), len(unusable)))


# --- build ------------------------------------------------------------------------------------

def races(forever_mask):
    if not forever_mask:
        return 0
    out = 0
    for bit, mask in RACES.items():
        if forever_mask & bit:
            out |= mask
    return 0 if out == ALL_RACES else out


WORD = re.compile(r"[a-z']+")
OLD_WORLD_ENTRIES = 17000       # the core's creatures below this are the old world's (Outland's and Northrend's come after)
COMMON = {"the", "of", "a", "an", "and", "young", "old", "elder", "lesser", "greater", "large", "small"}


def words(name):
    return {w for w in WORD.findall(name.lower()) if w not in COMMON and len(w) > 2}


class Looks:
    """The 3.3.5 creature a new NPC is drawn as: the same type and family (and, for people, the
    same side), the most name words shared, then the nearest spawn to where it stands."""

    def __init__(self, server_data, world):
        self.cols, templates = table(world, "creature_template")
        self.templates = {int(t["entry"]): t for t in templates}
        _, models = table(world, "creature_template_model")
        self.models = {}
        for m in models:
            self.models.setdefault(int(m["CreatureID"]), []).append(m)
        _, equips = table(world, "creature_equip_template")
        self.equips = {int(e["CreatureID"]): e for e in equips if int(e["ID"]) == 1}
        _, spawns = table(world, "creature")
        self.spawns = {}
        for s in spawns:
            self.spawns.setdefault(int(s["id1"]), []).append((int(s["map"]), float(s["position_x"]), float(s["position_y"]),
                                                             float(s["position_z"])))
        # Who a faction is friendly to, as the core reacts to a player: not a monster's, not the
        # side's enemy by its masks or by name (the players' own factions), and not below neutral
        # with the side's first race (a Human, an Orc) by its standing (Faction.dbc's base).
        rows, _ = dbc(os.path.join(server_data, "dbc", "Faction.dbc"))
        standing = {}
        for r in rows:
            for race, side in ((1, "A"), (2, "H")):
                for k in range(4):
                    if r[2 + k] & race:
                        base = struct.unpack("<i", struct.pack("<I", r[10 + k]))[0]
                        standing[(r[0], side)] = base
                        break
        rows, _ = dbc(os.path.join(server_data, "dbc", "FactionTemplate.dbc"))
        players = {"A": {1, 3, 4, 115, 1629}, "H": {2, 5, 6, 116, 1610}}       # (the players' templates' factions)
        self.side = {}
        for r in rows:
            faction, group, enemies, foes = r[1], r[3], r[5], set(r[6:10])
            self.side[r[0]] = "".join(side for side, mask in (("A", 3), ("H", 5))
                                      if not group & 8 and not enemies & mask and not foes & players[side]
                                      and standing.get((faction, side), 0) >= 0)
        rows, block = dbc(os.path.join(server_data, "dbc", "CreatureFamily.dbc"))
        self.families = {dbc_string(block, r[10]).lower(): r[0] for r in rows}
        # (not the invisible triggers, nor those only a holiday brings)
        _, events = table(world, "game_event_creature")
        holiday = {int(e["guid"]) for e in events}
        always = {int(s["id1"]) for s in spawns if int(s["guid"]) not in holiday}
        # the last words of names that are kinds of creature (four of the core's or more end in them:
        # Abomination, Raider), not a family's name (Ross, Wilson)
        ends = {}
        for t in self.templates.values():
            last = (WORD.findall(t["name"].lower()) or [""])[-1]
            ends.setdefault(last, []).append(int(t["type"]))
        self.kinds = {w for w, types in ends.items() if len(types) >= 4}
        self.kind_type = {w: max(set(types), key=types.count) for w, types in ends.items()}     # (what most of them are)
        self.candidates = [e for e in self.templates if e in always and e in self.models and
                           not int(self.templates[e]["flags_extra"]) & 128 and not int(self.templates[e]["npcflag"]) & 0xC000]
        # (nor spirit healers and guides, whom only the dead see)

    def family(self, name):
        return self.families.get((name or "").lower(), 0)

    def pick(self, npc):
        kind, family, side = npc["type"], self.family(npc["family"]), npc["friendly"]
        # (where nothing fits, the family goes first, then the side, then the type)
        for strict in ((kind, family, True), (kind, 0, True), (kind, 0, False), (0, 0, False)):
            best = self.best(npc, *strict)
            if best:
                return best

    def best(self, npc, kind, family, same_side):
        side = npc["friendly"]
        named = words(npc["name"])
        where = npc["spawns"][0] if npc["spawns"] else None
        best, best_score = None, None
        noun = (WORD.findall(npc["name"].lower()) or [""])[-1]
        noun = noun if noun in self.kinds else None
        for e in self.candidates:
            t = self.templates[e]
            # the same kind of creature by name (an Abomination) is the same kind of thing, whatever
            # type a person's tooltip gives it (a creature's own type and family stand)
            same_noun = noun and (WORD.findall(t["name"].lower()) or [""])[-1] == noun
            if kind and int(t["type"]) != kind and not (same_noun and kind == 7):
                continue
            if family and int(t["family"]) != family:
                continue
            their_side = self.side.get(int(t["faction"]), "")
            shared = len(named & words(t["name"]) - {noun})
            # a friend looks like a friend of the same side, a foe like a foe, where it's a person,
            # unless it's named for the same thing (its faction is its own either way)
            if same_side and not shared and not same_noun and (their_side != side if side else kind in (0, 6, 7) and their_side):
                continue
            # (a quest giver looks best as one of the core's quest givers)
            score = 60 * shared + (20 if their_side == side else 0) + (40 if same_noun else 0)
            # (a "person" named for a kind of creature that isn't one: an Abomination)
            score += 400 if same_noun and kind == 7 and self.kind_type[noun] != 7 and int(t["type"]) == self.kind_type[noun] else 0
            score += 30 if bool(npc.get("giver")) == bool(int(t["npcflag"]) & 2) else 0
            score -= abs((int(t["minlevel"]) + int(t["maxlevel"])) / 2 - sum(npc["level"]) / 2)
            if where:
                # the nearest on its own continent, and one of the old world's before Outland's and Northrend's
                near = min((math.hypot(x - where[1], y - where[2]) for m, x, y, _ in self.spawns[e] if m == where[0]), default=None)
                score -= 150 if near is None else min(near / 20, 100)
            score -= 40 if e >= OLD_WORLD_ENTRIES else 0
            if best_score is None or score > best_score:
                best, best_score = e, score
        return best


def build(server_data, world):
    quests = json.load(open(os.path.join(DATA, "quests.json"), encoding="utf-8"))
    experience = {int(k): v for k, v in json.load(open(os.path.join(DATA, "experience.json"), encoding="utf-8"))["xp"].items()}
    Q, ITEMS, NPCS, REWARDS = ({int(k): v for k, v in quests[x].items()} for x in ("quests", "items", "npcs", "rewards"))
    dbc_dir = os.path.join(server_data, "dbc")

    qcols, core_quests = table(world, "quest_template")
    core_ids = {int(q["ID"]) for q in core_quests}
    acols, _ = table(world, "quest_template_addon")
    icols, core_items = table(world, "item_template")
    lcols, loot = table(world, "creature_loot_template")
    looks = Looks(server_data, world)
    lootid = {e: int(t["lootid"]) for e, t in looks.templates.items()}
    names = {e: t["name"] for e, t in looks.templates.items()}
    names.update({n: v["name"] for n, v in NPCS.items() if v.get("new")})
    loot_by_entry = {}
    for r in loot:
        loot_by_entry.setdefault(int(r["Entry"]), []).append(r)

    xp_rows, _ = dbc(os.path.join(dbc_dir, "QuestXP.dbc"))
    quest_xp = {r[0]: r[1:] for r in xp_rows}
    area_rows, _ = dbc(os.path.join(dbc_dir, "AreaTable.dbc"))
    areas = {r[0] for r in area_rows}
    faction_rows, block = dbc(os.path.join(dbc_dir, "Faction.dbc"))
    factions = {dbc_string(block, r[23]): r[0] for r in faction_rows}
    display_rows, block = dbc(os.path.join(dbc_dir, "ItemDisplayInfo.dbc"))
    by_icon = {}
    for r in display_rows:
        by_icon.setdefault(dbc_string(block, r[5]).lower(), []).append(r[0])

    # Money and experience where Forever's data has none for a quest: the middle of what the core's
    # quests of the same level and kind pay.
    money = {}
    for q in core_quests:
        if int(q["RewardMoney"]) > 0:
            money.setdefault((int(q["QuestLevel"]), int(q["RewardXPDifficulty"])), []).append(int(q["RewardMoney"]))

    def pay(level, difficulty):
        for d in range(0, 6):
            for key in ((level, difficulty), (level - d, difficulty), (level + d, difficulty)):
                if key in money:
                    return int(statistics.median(money[key]))
        return 0

    def difficulty(level, xp, has_objectives):
        row = quest_xp.get(max(1, level))
        if not xp or not row:
            return 5 if has_objectives else 2
        return min(range(1, 9), key=lambda d: (abs(row[d] - xp), d))

    def display(name, icon=None, inventory_type=None):
        if icon and icon.lower() in by_icon:
            ids = by_icon[icon.lower()]
            used = [int(i["displayid"]) for i in core_items if int(i["displayid"]) in ids and
                    (inventory_type is None or int(i["InventoryType"]) == inventory_type)]
            return min(used) if used else min(ids)
        # no icon 3.3.5 has: the look of the core's quest item whose name is nearest (its last word first)
        mine = re.findall(r"[a-z]+", name.lower())
        best, score = None, 0
        for i in core_items:
            if int(i["class"]) not in (12, 15) or not int(i["displayid"]):
                continue
            theirs = set(re.findall(r"[a-z]+", i["name"].lower()))
            s = sum(2 if w == mine[-1] else 1 for w in mine if w in theirs and len(w) > 2)
            if s > score:
                best, score = i, s
        return int(best["displayid"]) if best else 7629

    out = ["-- WoW: Forever's new quests in the old zones (mod-forever-quests, tools/forever.py): generated, safe to\n"
           "-- run again. ChromieCraft's realm only (ctl.sh, realm_sql)."]

    def insert(t, cols, rows):
        if rows:
            out.append("INSERT INTO `%s` (%s) VALUES\n%s;" % (t, ", ".join("`%s`" % c for c in cols),
                       ",\n".join("(" + ", ".join(sqlrows.quote(r.get(c, 0)) for c in cols) + ")" for r in rows)))

    # The new NPCs: each the 3.3.5 creature nearest it in kind, under its own name, level, rank and
    # faction, where Forever has it.
    new_npcs = sorted(n for n, v in NPCS.items() if v.get("new"))
    givers = {n for q in Q.values() for n in group(q.get("startedBy"), 0) + group(q.get("finishedBy"), 0)}
    droppers = {d: [] for d in new_npcs}
    for i, g in ITEMS.items():
        for d in g.get("drops") or []:
            if d in droppers:
                droppers[d].append(i)
    templates, models, equips, spawn_rows, own_loot = [], [], [], [], []
    guid = FIRST_GUID
    ground = terrain.Terrain(os.path.join(server_data, "maps"))
    near_z = {}
    for e, ss in looks.spawns.items():
        for m, x, y, z in ss:
            near_z.setdefault((m, int(x // 20), int(y // 20)), []).append((x, y, z))
    look_of, friendly_of = {}, {}
    kill_targets = {c for q in Q.values() for c in first_ids(group(q.get("objectives") or [], 0))}
    for n in new_npcs:
        npc = dict(NPCS[n], giver=n in givers)
        source = looks.pick(npc)
        look_of[n] = source
        t = dict(looks.templates[source])
        their_side = looks.side.get(int(t["faction"]), "")
        # (one the data gives no side, drawn as one of a side's own, a guard say, and no quest's to kill:
        # that side's, as they look: Deathguard Kristof, at the waystation, isn't a monster)
        if npc["friendly"] == "" and their_side and n not in kill_targets:
            npc["friendly"] = their_side
        friendly_of[n] = npc["friendly"]
        rank = npc["rank"]
        t.update({"entry": n, "name": npc["name"], "subname": npc["subName"], "IconName": "", "gossip_menu_id": 0,
                  "minlevel": npc["level"][0], "maxlevel": npc["level"][1], "KillCredit1": 0, "KillCredit2": 0,
                  "difficulty_entry_1": 0, "difficulty_entry_2": 0, "difficulty_entry_3": 0,
                  "faction": int(t["faction"]) if their_side == npc["friendly"] else FACTIONS[npc["friendly"]],
                  "npcflag": 3 if n in givers else (1 if npc["friendly"] else 0), "rank": rank,
                  "HealthModifier": float(t["HealthModifier"]) * (3 if rank in (1, 2) and int(t["rank"]) not in (1, 2, 3) else 1),
                  "lootid": n if droppers[n] or lootid.get(source) else 0, "pickpocketloot": 0,
                  "AIName": "", "ScriptName": "", "VehicleId": 0, "PetSpellDataId": 0, "VerifiedBuild": 0})
        templates.append(t)
        for m in looks.models[source]:
            models.append(dict(m, CreatureID=n, VerifiedBuild=0))
        if source in looks.equips:
            equips.append(dict(looks.equips[source], CreatureID=n, VerifiedBuild=0))
        if t["lootid"]:
            for r in loot_by_entry.get(lootid.get(source) or -1, []):
                own_loot.append(dict(r, Entry=n, Comment="%s (as %s's, mod-forever-quests)" % (names.get(source), npc["name"])))
        # Where it stands: one spot for a quest giver or a named or rare creature (the one nearest
        # its spots' middle), every spot for the rest; on the ground there, or on the floor of the
        # building there if the core's own spawns close by stand well above or below the ground.
        points = npc["spawns"]
        single = n in givers or rank in (2, 3, 4) or len(npc["name"].split()) == 1
        if single and points:
            mx = sum(p[1] for p in points) / len(points)
            my = sum(p[2] for p in points) / len(points)
            points = [min(points, key=lambda p: math.hypot(p[1] - mx, p[2] - my))]
        if len(points) > 40:
            points = points[::math.ceil(len(points) / 40)]
        for map_id, x, y in points:
            z = ground.height(map_id, x, y)
            close = [c for gx in (-1, 0, 1) for gy in (-1, 0, 1)
                     for c in near_z.get((map_id, int(x // 20) + gx, int(y // 20) + gy), []) if math.hypot(c[0] - x, c[1] - y) < 12]
            if close:
                cz = min(close, key=lambda c: math.hypot(c[0] - x, c[1] - y))[2]
                if z is None or abs(cz - z) > 2.5:
                    z = cz
            if z is None:
                continue
            hostile = npc["friendly"] == ""
            spawn_rows.append({"guid": guid, "id": n, "map": map_id, "zoneId": 0, "areaId": 0, "spawnMask": 1,
                               "phaseMask": 1, "equipment_id": 1 if source in looks.equips else 0,
                               "position_x": x, "position_y": y, "position_z": round(z + 0.1, 2),
                               "orientation": round((guid * 2.39996) % 6.28318, 3), "spawntimesecs": 300,
                               "wander_distance": 5 if hostile and not single else 0, "currentwaypoint": 0, "curhealth": 1, "curmana": 0,
                               "MovementType": 1 if hostile and not single else 0, "npcflag": 0, "unit_flags": 0, "dynamicflags": 0,
                               "ScriptName": "", "VerifiedBuild": 0, "CreateObject": 0,
                               "Comment": "%s (WoW: Forever, mod-forever-quests)" % npc["name"]})
            guid += 1

    ids = sorted(Q)
    id_list = ", ".join(map(str, ids))
    for t, key in (("quest_template", "ID"), ("quest_template_addon", "ID"), ("quest_request_items", "ID"), ("quest_offer_reward", "ID")):
        out.append("DELETE FROM `%s` WHERE `%s` IN (%s);" % (t, key, id_list))
    for t in ("creature_queststarter", "creature_questender", "gameobject_queststarter", "gameobject_questender"):
        out.append("DELETE FROM `%s` WHERE `quest` IN (%s);" % (t, id_list))
    if new_npcs:
        npc_list = ", ".join(map(str, new_npcs))
        out.append("\n-- The new people and creatures, each drawn as a 3.3.5 creature (as listed below: Forever's, then the look's)")
        out.append("DELETE FROM `creature` WHERE `guid` BETWEEN %d AND %d;" % (FIRST_GUID, FIRST_GUID + 99999))
        for t, key in (("creature_template", "entry"), ("creature_template_model", "CreatureID"), ("creature_equip_template", "CreatureID"),
                       ("creature_loot_template", "Entry")):
            out.append("DELETE FROM `%s` WHERE `%s` IN (%s);" % (t, key, npc_list))
        for n in new_npcs:
            out.append("-- %s (%d): %s (%d)" % (NPCS[n]["name"], n, names.get(look_of[n]), look_of[n]))
        insert("creature_template", looks.cols, templates)
        insert("creature_template_model", ["CreatureID", "Idx", "CreatureDisplayID", "DisplayScale", "Probability", "VerifiedBuild"], models)
        insert("creature_equip_template", ["CreatureID", "ID", "ItemID1", "ItemID2", "ItemID3", "VerifiedBuild"], equips)
        # (the core's updates since its base SQL name the creature column `id`: 2026_06_16_00)
        insert("creature", ["guid", "id", "map", "zoneId", "areaId", "spawnMask", "phaseMask", "equipment_id",
                            "position_x", "position_y", "position_z", "orientation", "spawntimesecs", "wander_distance",
                            "currentwaypoint", "curhealth", "curmana", "MovementType", "npcflag", "unit_flags", "dynamicflags",
                            "ScriptName", "VerifiedBuild", "CreateObject", "Comment"], spawn_rows)

    template, addons, requests, offers = [], [], [], []
    starters, enders, object_starters = [], [], []
    chain_next = {}
    for qid in ids:
        q = Q[qid]
        for p in q.get("preQuestSingle") or []:
            prev = Q.get(p)
            if prev and set(group(prev.get("finishedBy"), 0)) & set(group(q.get("startedBy"), 0)):
                chain_next[p] = qid
    for qid in ids:
        q = Q[qid]
        page = q["page"]
        level = page["level"] or q.get("questLevel") or 1
        min_level = page["min_level"] or q.get("requiredLevel") or 1
        objectives = q.get("objectives") or []
        kills = first_ids(group(objectives, 0))
        collect = first_ids(group(objectives, 2))
        counts = {i: c for i, c in page["need_items"]}
        goals = {name: c for name, c in page["need_goals"]}
        counts.update({c: goals[names[c]] for c in kills if names.get(c) in goals})
        # (a page with no experience has no rewards from Wowhead's data at all: its money is unknown too)
        d = difficulty(level, page["xp"] or experience.get(qid), bool(kills or collect))
        coin = page["money"] if page["xp"] else pay(level, d)
        zone = q.get("zoneOrSort") if isinstance(q.get("zoneOrSort"), int) else 0
        if zone == 0 or zone > 0 and zone not in areas:
            # one of Forever's new areas: the zone of the one who gives it
            zone = next((NPCS[n]["zoneID"] for n in group(q.get("startedBy"), 0) if NPCS.get(n, {}).get("zoneID") in areas), 0)
        enders_here = group(q.get("finishedBy"), 0)
        row = {c: 0 for c in qcols}
        row.update({
            "ID": qid, "QuestType": 2, "QuestLevel": level, "MinLevel": min_level, "QuestSortID": zone,
            "RewardXPDifficulty": d, "RewardMoney": coin, "AllowableRaces": races(q.get("requiredRaces")),
            "Flags": QUEST_FLAGS_SHARABLE if page["shareable"] else 0,
            "StartItem": q.get("sourceItemId") or 0, "RewardNextQuest": chain_next.get(qid, 0),
            "LogTitle": q["name"], "LogDescription": page["objectives_text"],
            "QuestDescription": page["description"] or page["objectives_text"], "AreaDescription": "", "QuestCompletionLog": "",
            "ObjectiveText1": "", "ObjectiveText2": "", "ObjectiveText3": "", "ObjectiveText4": "", "VerifiedBuild": 0,
        })
        for n, c in enumerate(kills[:4], 1):
            row["RequiredNpcOrGo%d" % n] = c
            row["RequiredNpcOrGoCount%d" % n] = counts.get(c) or 1
        for n, i in enumerate(collect[:6], 1):
            row["RequiredItemId%d" % n] = i
            row["RequiredItemCount%d" % n] = counts.get(i) or 1
        for n, (i, c) in enumerate(page["reward_items"][:4], 1):
            row["RewardItem%d" % n], row["RewardAmount%d" % n] = i, c
        for n, (i, c) in enumerate(page["reward_choice"][:6], 1):
            row["RewardChoiceItemID%d" % n], row["RewardChoiceItemQuantity%d" % n] = i, c
        for n, (faction, value) in enumerate([r for r in page["reputation"] if r[0] in factions][:5], 1):
            # the amount itself (RewardFactionOverride is a hundredth of a point), not a QuestFactionReward step
            row["RewardFactionID%d" % n], row["RewardFactionOverride%d" % n] = factions[faction], value * 100
        template.append(row)
        addon = {c: 0 for c in acols}
        pre = (q.get("preQuestSingle") or []) + (q.get("preQuestGroup") or [])
        # (a breadcrumb only to a quest that's here: Forever's or the core's; the world server names any other)
        crumb = q.get("breadcrumbForQuestId") or 0
        if crumb not in Q and crumb not in core_ids:
            crumb = 0
        addon.update({"ID": qid, "PrevQuestID": pre[0] if pre else 0, "ProvidedItemCount": 1 if q.get("sourceItemId") else 0,
                      "ExclusiveGroup": 0, "BreadcrumbForQuestId": crumb})
        addons.append(addon)
        if page["progress"]:
            requests.append({"ID": qid, "EmoteOnComplete": 1, "EmoteOnIncomplete": 1, "CompletionText": page["progress"], "VerifiedBuild": 0})
        offers.append({"ID": qid, "Emote1": 1, "Emote2": 0, "Emote3": 0, "Emote4": 0, "EmoteDelay1": 0, "EmoteDelay2": 0,
                       "EmoteDelay3": 0, "EmoteDelay4": 0, "RewardText": page["completion"] or NO_HAND_IN, "VerifiedBuild": 0})
        starters += [{"id": n, "quest": qid} for n in group(q.get("startedBy"), 0)]
        object_starters += [{"id": o, "quest": qid} for o in group(q.get("startedBy"), 1)]
        enders += [{"id": n, "quest": qid} for n in enders_here]

    out.append("\n-- The quests")
    insert("quest_template", qcols, template)
    insert("quest_template_addon", acols, addons)
    insert("quest_request_items", ["ID", "EmoteOnComplete", "EmoteOnIncomplete", "CompletionText", "VerifiedBuild"], requests)
    insert("quest_offer_reward", ["ID", "Emote1", "Emote2", "Emote3", "Emote4", "EmoteDelay1", "EmoteDelay2", "EmoteDelay3",
                                  "EmoteDelay4", "RewardText", "VerifiedBuild"], offers)
    out.append("\n-- Who gives and takes them; the core's own among them who give no quest there are made quest givers")
    plain = sorted({r["id"] for r in starters + enders if r["id"] in looks.templates and not int(looks.templates[r["id"]]["npcflag"]) & 2})
    if plain:
        out.append("UPDATE `creature_template` SET `npcflag` = `npcflag` | 2 WHERE `entry` IN (%s);" % ", ".join(map(str, plain)))
    insert("creature_queststarter", ["id", "quest"], starters)
    insert("gameobject_queststarter", ["id", "quest"], object_starters)
    insert("creature_questender", ["id", "quest"], enders)

    # The items: the ones collected, carried and started from (Forever's quest items), and the rewards.
    items = []
    collected = {}
    for qid in ids:
        counts = dict(Q[qid]["page"]["need_items"])
        for i in first_ids(group(Q[qid].get("objectives"), 2)):
            collected[i] = max(collected.get(i, 1), counts.get(i) or 1)
    blank = {c: 0 for c in icols}
    blank.update({"SoundOverrideSubclass": -1, "Quality": 1, "BuyCount": 1, "stackable": 1, "description": "", "ScriptName": "",
                  "VerifiedBuild": 0, "RequiredDisenchantSkill": -1, "Material": -1, "sheath": 0, "maxcount": 0})
    for n in range(1, 6):
        blank["spellcooldown_%d" % n] = -1
        blank["spellcategorycooldown_%d" % n] = -1
    for i in sorted(set(ITEMS) | set(REWARDS)):
        row = dict(blank, entry=i)
        if i in REWARDS:
            g = REWARDS[i]
            row.update({"name": g["name"], "class": g["class"], "subclass": g["subclass"], "Quality": g["quality"],
                        "ItemLevel": g["item_level"], "RequiredLevel": g["required_level"], "bonding": g["bonding"],
                        "SellPrice": g["sell"], "BuyPrice": g["buy"], "InventoryType": g["inventory"], "Material": g["material"],
                        "sheath": g["sheath"], "stackable": g["stack"], "maxcount": g["maxcount"], "ContainerSlots": g["bag_slots"],
                        "AllowableClass": g["allowable_class"] or -1, "AllowableRace": g["allowable_race"] or -1,
                        "displayid": display(g["name"], g.get("icon"), g["inventory"]), "MaxDurability": g["durability"],
                        "armor": g["armor"], "delay": g["delay"] or int(g["speed"] * 1000), "startquest": g["start_quest"]})
            if g.get("dmg"):
                row.update({"dmg_min1": g["dmg"][0], "dmg_max1": g["dmg"][1], "dmg_type1": g.get("dmg_school", 0)})
            for key in wowhead.RESISTANCES.values():
                row[key] = g.get(key, 0)
            stats = {}
            for stat, value in g["stats"]:
                stats[stat] = stats.get(stat, 0) + value
            for n, (stat, value) in enumerate(sorted(stats.items())[:10], 1):
                row["stat_type%d" % n], row["stat_value%d" % n] = stat, value
            for n, spell in enumerate(g["use"][:5], 1):
                row["spellid_%d" % n], row["spelltrigger_%d" % n] = spell, 0
                row["spellcharges_%d" % n] = -1 if g["class"] == 0 else 0
        else:
            g = ITEMS[i]
            start = g.get("startQuest") or 0
            row.update({"name": g["name"], "class": 12, "subclass": 0, "displayid": display(g["name"], g.get("icon")),
                        "bonding": ITEM_BIND_QUEST if not start else ITEM_BIND_PICKUP, "startquest": start,
                        "maxcount": collected.get(i, 1), "stackable": collected.get(i, 1)})
        items.append(row)
    out.append("\n-- Their items: Forever's ids, the looks of the 3.3.5 items with the same icons")
    out.append("DELETE FROM `item_template` WHERE `entry` IN (%s);" % ", ".join(str(r["entry"]) for r in items))
    insert("item_template", icols, items)

    # Who drops them: Forever's own sources (QuestieDB's npcDrops); the chances aren't known, so a
    # quest item drops as often as the core's quest items commonly do. A friendly person's is asked of
    # them instead (GIVE_MENU).
    def friendly(c):
        if c in NPCS and NPCS[c].get("new"):
            return friendly_of.get(c, "") != ""
        t = looks.templates.get(c)
        return bool(t and looks.side.get(int(t["faction"]), ""))
    collected_by = {}
    for qid in ids:
        for i in first_ids(group(Q[qid].get("objectives") or [], 2)):
            collected_by.setdefault(i, []).append(qid)
    loot_rows, creature_updates, gives = [], set(), []
    for i in sorted(ITEMS):
        g = ITEMS[i]
        drops = [d for d in g.get("drops") or [] if d in lootid or d in NPCS]
        if not drops or i not in collected and not g.get("startQuest"):
            continue
        # an item that starts a quest drops for anyone who hasn't taken it (the core leaves it out after),
        # and seldom where many creatures carry it
        starts = bool(g.get("startQuest"))
        for c in [d for d in drops if not starts and friendly(d) and collected_by.get(i)]:
            gives.append((c, i, collected_by[i]))
        drops = [d for d in drops if not any(c == d and gi == i for c, gi, _ in gives)]
        for c in drops:
            new = c in NPCS and NPCS[c].get("new")
            entry = c if new else (lootid.get(c) or c)
            if not new and not lootid.get(c):
                creature_updates.add(c)
            chance = (100 if len(drops) == 1 else 8) if starts else (60 if len(drops) <= 2 else 35)
            loot_rows.append({"Entry": entry, "Item": i, "Reference": 0, "Chance": chance, "QuestRequired": 0 if starts else 1,
                              "LootMode": 1, "GroupId": 0, "MinCount": 1, "MaxCount": 1,
                              "Comment": "%s - %s (mod-forever-quests)" % (names.get(c, c), g["name"])})
    out.append("\n-- Who drops them")
    out.append("DELETE FROM `creature_loot_template` WHERE `Item` IN (%s);" % ", ".join(str(i) for i in sorted(ITEMS)))
    for c in sorted(creature_updates):
        out.append("UPDATE `creature_template` SET `lootid` = `entry` WHERE `entry` = %d AND `lootid` = 0;" % c)
    insert("creature_loot_template", lcols, own_loot + loot_rows)

    # Asked of them: an option in their menu (theirs, or one made for them), shown to one with the quest in
    # the log and without the item; their SmartAI hands it over.
    out.append("\n-- Asked of the friendly: an item Forever's data has them \"drop\", given when asked")
    out.append("DELETE FROM `gossip_menu` WHERE `MenuID` BETWEEN %d AND %d;" % (GIVE_MENU, GIVE_MENU + 99))
    out.append("DELETE FROM `npc_text` WHERE `ID` BETWEEN %d AND %d;" % (GIVE_MENU, GIVE_MENU + 99))
    out.append("DELETE FROM `gossip_menu_option` WHERE `OptionID` BETWEEN %d AND %d;" % (GIVE_OPTION, GIVE_OPTION + 39))
    out.append("DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 15 AND `SourceEntry` BETWEEN %d AND %d;" % (GIVE_OPTION, GIVE_OPTION + 39))
    out.append("DELETE FROM `smart_scripts` WHERE `source_type` = 0 AND `id` BETWEEN %d AND %d;" % (GIVE_EVENT, GIVE_EVENT + 79))
    new_templates = {int(t["entry"]): t for t in templates}
    menus, texts, options, conds, smart = [], [], [], [], []
    menu_of = {}
    for n, (c, i, quests) in enumerate(gives):
        option = GIVE_OPTION + n
        menu = int(new_templates[c]["gossip_menu_id"]) if c in new_templates else int(looks.templates[c]["gossip_menu_id"])
        if not menu:
            menu = menu_of.get(c) or GIVE_MENU + len(menu_of)
            if c not in menu_of:
                menu_of[c] = menu
                menus.append("(%d, %d)" % (menu, menu))
                texts.append("(%d, %s, %s, 1)" % (menu, sqlrows.quote("What is it, $c?"), sqlrows.quote("What is it, $c?")))
        holder = NPCS[c]["name"] if c in NPCS else names.get(c, str(c))
        # ("Kristof's Report" asked of Deathguard Kristof: "your report")
        asked = ITEMS[i]["name"].replace(holder.split()[-1] + "'s", "your")
        asked = asked[:5] + asked[5:].lower() if asked.startswith("your ") else asked
        options.append("(%d, %d, 0, %s, 0, 1, 1, 0, 0, 0, 0, '', 0)" % (menu, option, sqlrows.quote("I'm here for %s." % asked)))
        for g_, qid in enumerate(quests):
            note = sqlrows.quote("%s gives %s (mod-forever-quests)" % (holder, ITEMS[i]["name"]))
            conds.append("(15, %d, %d, 0, %d, 9, 0, %d, 0, 0, 0, %s)" % (menu, option, g_, qid, note))
            conds.append("(15, %d, %d, 0, %d, 2, 0, %d, 1, 0, 1, %s)" % (menu, option, g_, i, note))
            conds.append("(15, %d, %d, 0, %d, 31, 1, 3, %d, 0, 0, %s)" % (menu, option, g_, c, note))
        smart.append("(%d, 0, %d, %d, 62, 0, 100, 0, %d, %d, 0, 0, 0, 0, 56, %d, 1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, %s)"
                     % (c, GIVE_EVENT + 2 * n, GIVE_EVENT + 2 * n + 1, menu, option, i, sqlrows.quote("%s - gives %s" % (holder, ITEMS[i]["name"]))))
        smart.append("(%d, 0, %d, 0, 61, 0, 100, 0, 0, 0, 0, 0, 0, 0, 72, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, %s)"
                     % (c, GIVE_EVENT + 2 * n + 1, sqlrows.quote("%s - closes the menu" % holder)))
    if gives:
        if menus:
            out.append("INSERT INTO `gossip_menu` (`MenuID`, `TextID`) VALUES %s;" % ", ".join(menus))
            out.append("INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES %s;" % ", ".join(texts))
            for c, menu in sorted(menu_of.items()):
                out.append("UPDATE `creature_template` SET `gossip_menu_id` = %d, `npcflag` = `npcflag` | 1 WHERE `entry` = %d;" % (menu, c))
        out.append("INSERT INTO `gossip_menu_option` (`MenuID`, `OptionID`, `OptionIcon`, `OptionText`, `OptionBroadcastTextID`, "
                   "`OptionType`, `OptionNpcFlag`, `ActionMenuID`, `ActionPoiID`, `BoxCoded`, `BoxMoney`, `BoxText`, "
                   "`BoxBroadcastTextID`) VALUES\n%s;" % ",\n".join(options))
        out.append("INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, "
                   "`ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, "
                   "`NegativeCondition`, `Comment`) VALUES\n%s;" % ",\n".join(conds))
        out.append("UPDATE `creature_template` SET `AIName` = 'SmartAI' WHERE `entry` IN (%s) AND `ScriptName` = '';"
                   % ", ".join(str(c) for c in sorted({c for c, _, _ in gives})))
        out.append("INSERT INTO `smart_scripts` (`entryorguid`, `source_type`, `id`, `link`, `event_type`, `event_phase_mask`, "
                   "`event_chance`, `event_flags`, `event_param1`, `event_param2`, `event_param3`, `event_param4`, `event_param5`, "
                   "`event_param6`, `action_type`, `action_param1`, `action_param2`, `action_param3`, `action_param4`, "
                   "`action_param5`, `action_param6`, `target_type`, `target_param1`, `target_param2`, `target_param3`, "
                   "`target_param4`, `target_x`, `target_y`, `target_z`, `target_o`, `comment`) VALUES\n%s;" % ",\n".join(smart))
    os.makedirs(os.path.dirname(SQL_OUT), exist_ok=True)
    with open(SQL_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("%d quests, %d new NPCs (%d spawns), %d items, %d drops: %s" % (
        len(ids), len(new_npcs), len(spawn_rows), len(items), len(loot_rows), os.path.relpath(SQL_OUT, MODULE)))


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[1] == "import":
        import_(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif len(sys.argv) == 4 and sys.argv[1] == "build":
        build(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(2)
